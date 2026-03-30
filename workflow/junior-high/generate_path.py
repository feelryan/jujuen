import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TAIWAN_DIR = BASE_DIR / "taiwan"
OUTPUT_PATH = TAIWAN_DIR / "nature-path.json"

SUBJECT_SLUG = "nature"  # 科目代碼，用在檔名中

GRADES = [
    {
        "id": "7",
        "t": "7年級",
        "c": "七年級",
        "en": "Grade 7",
        "grade_key": "7th",
    },
    {
        "id": "8",
        "t": "8年級",
        "c": "八年級",
        "en": "Grade 8",
        "grade_key": "8th",
    },
    {
        "id": "9",
        "t": "9年級",
        "c": "九年級",
        "en": "Grade 9",
        "grade_key": "9th",
    },
]

# 四個考試期別與對應的「考題」名稱
PHASES = [
    {"key": "mid1", "t": "期中1", "quiz_t": "期中1考題", "en": "Midterm 1", "quiz_en": "Midterm 1 quiz"},
    {"key": "mid2", "t": "期中2", "quiz_t": "期中2考題", "en": "Midterm 2", "quiz_en": "Midterm 2 quiz"},
    {"key": "final2", "t": "期末2", "quiz_t": "期末2考題", "en": "Final 2", "quiz_en": "Final 2 quiz"},
    {"key": "final3", "t": "期末3", "quiz_t": "期末3考題", "en": "Final 3", "quiz_en": "Final 3 quiz"},
]

GITHUB_BASE = "https://github.com/feelryan/jujuen/blob/junior-high/taiwan"


def build_items() -> list[dict]:
    items: list[dict] = []

    for grade in GRADES:
        grade_id = f"tw-math-{grade['id']}"

        # 年級節點（根節點）
        items.append(
            {
                "id": grade_id,
                "parent": None,
                "t": grade["t"],
                "c": grade["c"],
                "p": "",
                "z": "",
                "en": grade["en"],
            }
        )

        prev_exam_id: str | None = None

        for phase in PHASES:
            phase_key = phase["key"]

            # 考試節點（期中1 / 期中2 / 期末2 / 期末3）
            exam_id = f"{grade['id']}-{phase_key}"

            # 第一個考試的 parent 是年級，其餘依序接在上一個考試之下
            parent_for_exam = grade_id if prev_exam_id is None else prev_exam_id

            # 共用的檔名基底: ${科目}_${年級}_${期別}
            base_name = f"{SUBJECT_SLUG}_{grade['grade_key']}_{phase['t']}"

            # 1) 考試節點本身：連到 Words 用的 JSON
            #    pointTo: github/json + renderObject=Words，檔名為 ${科目}_${年級}_${期別}.json
            json_filename = f"{base_name}.json"
            json_url = f"{GITHUB_BASE}/{json_filename}"

            items.append(
                {
                    "id": exam_id,
                    "parent": parent_for_exam,
                    "t": phase["t"],
                    "c": phase["t"],
                    "p": "",
                    "z": "",
                    "en": phase["en"],
                    "pointTo": {
                        "type": "document",
                        "data": "github/json",
                        "dataLocation": json_url,
                        "renderObject": "Words",
                    },
                }
            )

            # 2) 對應的說明文件（Markdown）：${科目}_${年級}_${期別}.md
            md_filename = f"{base_name}.md"
            md_url = f"{GITHUB_BASE}/{md_filename}"

            md_node_id = f"{exam_id}-md"
            items.append(
                {
                    "id": md_node_id,
                    "parent": exam_id,
                    "t": f"{phase['t']}(md)",
                    "c": f"{phase['t']}(md)",
                    "p": "",
                    "z": "",
                    "en": f"{phase['en']} (Markdown)",
                    "pointTo": {
                        "type": "document",
                        "data": "github/md",
                        "dataLocation": md_url,
                    },
                }
            )

            # 3) 該期別的「考題」節點: ${科目}_${年級}_${期別考題}.md（維持原本設定）
            quiz_id = f"{grade['id']}-{phase_key}-quiz"
            quiz_filename = f"{SUBJECT_SLUG}_{grade['grade_key']}_{phase['quiz_t']}.json"
            quiz_url = f"{GITHUB_BASE}/{quiz_filename}"

            items.append(
                {
                    "id": quiz_id,
                    "parent": exam_id,
                    "t": phase["quiz_t"],
                    "c": phase["quiz_t"],
                    "p": "",
                    "z": "",
                    "en": phase["quiz_en"],
                    "pointTo": {
                        "type": "document",
                        "data": "github/json",
                        "dataLocation": quiz_url,
                        "renderObject": "Question",
                    },
                }
            )

            prev_exam_id = exam_id

    return items


def main() -> None:
    TAIWAN_DIR.mkdir(parents=True, exist_ok=True)

    data = {
        "id": "taiwan-math-path",
        "title": "台灣國中數學",
        "items": build_items(),
    }

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Generated math-path.json at: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
