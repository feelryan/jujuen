# Supported Files and Components

The learning content of this site is woven together by three core concepts:

- **MenuPath (Learning Path Map)**: A roadmap made of nodes, usually used for chapter navigation or learning progress.
- **Category (Topic List)**: A list that shows topics as rows; each row is a topic.
- **Document (Content Page)**: The actual page the learner reads, such as explanations, exercises, PDF handouts, videos, web pages, or Notion pages.

Every node or list item can use a common field **`pointTo`** to "point" to the next target (another MenuPath, Category, or Document).

> By adding or editing JSON configuration files, you can keep extending the learning paths without changing any code.

---

## 1. `pointTo`: How to Define "Where to Go Next"?

In all JSON files, whenever an item has a `pointTo` field, it means this item is clickable and will lead to the next content. The `pointTo` object has three key fields:

- `type`: The type of target to go to
  - `document`: Go to an actual content page
  - `category`: Go to a topic list (Category)
  - `menupath`: Go to another learning path map (MenuPath)
- `data`: The format / source type of the content
	- `github/json`: A JSON data file stored on GitHub
	- `github/md`: A Markdown text file stored on GitHub
	- `github/image`: An image file stored on GitHub
	- `github/pdf`: A PDF file stored on GitHub
	- `web/page`: A normal web page
	- `youtube`: A YouTube video
	- `notion`: A public, embeddable Notion page (an embeddable URL)
- `dataLocation`: The actual URL
	- GitHub / normal web pages / YouTube: use a full URL that can be opened directly in a browser
	- Notion: use a public share URL that supports embedding (usually the link you copy from Notion after turning on "Share to web" and generating an embeddable link that contains `ebd`, e.g. `https://chiseled-grain-cc5.notion.site/ebd//xxxxxxxxxxxxxxxxxx`)

As long as you know how to fill these three fields, you can make any node or list item lead to the next step you want.

---

## 2. MenuPath: Learning Path Map JSON Format

You can think of a MenuPath as a "map" with many nodes (cards) on it.

- `id`: The identifier of this map.
- `title`: The title of this map (shown on the screen).
- `items`: All nodes on the map; each node is one learning step.

Common fields for each node (`item`):

- `id`: The identifier of this node.
- `parent`: The `id` of its parent node, used to determine levels and connector lines. Use `null` for top-level nodes.
- `t` / `c` / `p` / `z` / `en`: Traditional Chinese, Simplified Chinese, Pinyin, Zhuyin, and English explanation. (Only `t` is required.)
- `pointTo`: Optional. If present, the node becomes clickable and will lead to another content.

### 2.1 Basic MenuPath JSON Example

Recommended workflow:

- Create a branch in the [JuJuEn](https://github.com/feelryan/jujuen) GitHub repository and add a JSON file with content like the example below.
- Replace `https://github.com/feelryan/jujuen/blob/{YOUR_BRANCH}/menu-path.json` with your own GitHub path.

```json
{
	"id": "ch1-intro-menupath",
	"title": "第 1 章：入門導覽",
	"items": [
		{
			"id": "ch1-root",
			"parent": null,
			"t": "入門導覽",
			"c": "入门导览",
			"p": "rù mén dǎo lǎn",
			"z": "ㄖㄨˋ ㄇㄣˊ ㄉㄠˇ ㄌㄢˇ",
			"en": "Chapter 1 overview",
			"pointTo": {
				"type": "document",
				"data": "github/md",
				"dataLocation": "https://github.com/feelryan/jujuen/blob/{YOUR_BRANCH}/overview.md"
			}
		},
		{
			"id": "ch1-basic-category",
			"parent": "ch1-root",
			"t": "常用字分類",
			"c": "常用字分类",
			"p": "cháng yòng zì fēn lèi",
			"z": "ㄔㄤˊ ㄩㄥˋ ㄗˋ ㄈㄣ ㄌㄟˋ",
			"en": "Common characters categories",
			"pointTo": {
				"type": "category",
				"data": "github/json",
				"dataLocation": "https://github.com/feelryan/jujuen/blob/{YOUR_BRANCH}/common-chars-category.json"
			}
		},
		{
			"id": "ch1-next-menupath",
			"parent": "ch1-root",
			"t": "進入第 2 章",
			"c": "进入第 2 章",
			"p": "jìn rù dì èr zhāng",
			"z": "ㄐㄧㄣˋ ㄖㄨˋ ㄉㄧˋ ㄦˋ ㄓㄤ",
			"en": "Go to chapter 2 menu",
			"pointTo": {
				"type": "menupath",
				"data": "github/json",
				"dataLocation": "https://github.com/feelryan/jujuen/blob/{YOUR_BRANCH}/ch2-menupath.json"
			}
		}
	]
}
```

Explanation:

- `parent` controls the hierarchy of nodes and how connector lines are drawn.
- The first item points to a Markdown document (`type=document`, `data=github/md`).
- The second item points to a Category JSON (`type=category`).
- The third item points to **another MenuPath JSON** (`type=menupath`), so the path can continue.

---

## 3. Category: Topic List JSON Format

A Category is a "topic list", such as "Daily Life" or "Travel Expressions". Each row can lead to more detailed content.

Common fields:

- `id`: Identifier of this topic list.
- `title`: Title of the list.
- `items`: All topic items in the list.

Common fields for each item in the list:

- `id`: Identifier of this topic item.
- `t` / `c` / `p` / `z` / `en`: Same meaning as in MenuPath nodes. (Only `t` is required.)
- `pointTo`: Optional. If present, the row becomes an entry that leads to another document or path.

### 3.1 Category JSON Example

Recommended workflow:

- In the same GitHub repository, create a JSON file for Category, with content like the example below.
- Replace `https://github.com/feelryan/jujuen/blob/{YOUR_BRANCH}/category.json` with your actual path.

```json
{
	"id": "common-chars-category",
	"title": "常用字主題分類",
	"items": [
		{
			"id": "daily-life",
			"t": "日常生活",
			"c": "日常生活",
			"p": "rì cháng shēng huó",
			"z": "ㄖˋ ㄔㄤˊ ㄕㄥ ㄏㄨㄛˊ",
			"en": "Daily life",
			"pointTo": {
				"type": "document",
				"data": "github/json",
				"dataLocation": "https://github.com/feelryan/jujuen/blob/{YOUR_BRANCH}/daily-life-words.json",
				"renderObject": "Words"
			}
		},
		{
			"id": "travel-basic",
			"t": "旅行用語",
			"c": "旅行用语",
			"p": "lǚ xíng yòng yǔ",
			"z": "ㄌㄩˇ ㄒㄧㄥˊ ㄩㄥˋ ㄩˇ",
			"en": "Travel basics",
			"pointTo": {
				"type": "menupath",
				"data": "github/json",
				"dataLocation": "https://github.com/feelryan/jujuen/blob/{YOUR_BRANCH}/travel-menupath.json"
			}
		}
	]
}
```

Explanation:

- Each row in the Category can have a `pointTo`, turning the list into the next layer of entry points.
- A row can directly point to a Document (`type=document`) or to another MenuPath, forming structures like `MenuPath → Category → MenuPath → Document → …`.

---

## 4. Examples of Different Document Links

### 4.1 Linking to a GitHub JSON Document

- When `type` is `"document"` and `data` is `"github/json"`, you usually also need `"renderObject"` to tell the system how to render the content. Currently, supported values are `Words` and `Question`.

```json
{
	"pointTo": {
		"type": "document",
		"data": "github/json",
		"dataLocation": "https://github.com/feelryan/jujuen/blob/{YOUR_BRANCH}/ch1-quiz.json",
        "renderObject": "Question"
	}
}
```

Explanation:

- Suitable for quizzes, word lists, or other structured data.
- Replace the URL with your own GitHub JSON file URL.

### 4.2 Linking to a GitHub Markdown (.md) File

```json
{
	"pointTo": {
		"type": "document",
		"data": "github/md",
		"dataLocation": "https://github.com/feelryan/jujuen/blob/{YOUR_BRANCH}/overview.md"
	}
}
```

Rules:

- Use any GitHub file URL that opens in a browser (e.g. `https://github.com/.../blob/...`).
- If images referenced in the Markdown are in the same repository, the system will try to display them as well.

### 4.3 Linking to a GitHub PDF

```json
{
	"pointTo": {
		"type": "document",
		"data": "github/pdf",
		"dataLocation": "https://github.com/feelryan/jujuen/blob/{YOUR_BRANCH}/ch1-handout.pdf"
	}
}
```

The system will open the PDF directly in the page for easy reading of handouts or slides.

### 4.4 Linking to a GitHub Image

```json
{
	"pointTo": {
		"type": "document",
		"data": "github/image",
		"dataLocation": "https://github.com/feelryan/jujuen/blob/{YOUR_BRANCH}/example.png"
	}
}
```

Good for displaying a single chart, diagram, or illustration.

### 4.5 Linking to a YouTube Video

```json
{
	"pointTo": {
		"type": "document",
		"data": "youtube",
		"dataLocation": "https://www.youtube.com/watch?v=XXXXXXXXXXX"
	}
}
```

The system will embed a video player and play the video directly in the page.

### 4.6 Linking to a Public Notion Page

```json
{
	"pointTo": {
		"type": "document",
		"data": "notion",
		"dataLocation": "https://chiseled-grain-cc5.notion.site/ebd//xxxxxxxxxxxxxxxxxx"
	}
}
```

Explanation:

- First, turn on "Share to web" for the page in Notion, then copy the share link into `dataLocation`.
- The URL must be a public embeddable link that other sites can embed; otherwise the system cannot show the Notion content.
- The public embeddable link usually contains the string `ebd`, for example: `https://chiseled-grain-cc5.notion.site/ebd//xxxxxxxxxxxxxxxxxx`.

### 4.7 Linking to a Normal Web Page

```json
{
	"pointTo": {
		"type": "document",
		"data": "web/page",
		"dataLocation": "https://example.com/your-article-or-tool"
	}
}
```

Explanation:

- Good for linking to online articles, tools, or interactive learning materials.
- Use a full URL that opens in a browser; the system will help open it in a new window or embedded view.

---

## 5. How to Make the Learning Paths Infinitely Extendable

Using the structure above, you can design learning paths in a data-driven way:

1. **Top-level MenuPath**: Acts as chapter or topic navigation. Each node can:
	 - Point directly to a document (Markdown / PDF / JSON document).
	 - Point to a Category list (such as common characters or question types).
	 - Point to another MenuPath (next chapter or an advanced route).
2. **Each row in a Category list** can also:
	 - Point to a quiz JSON or word list JSON.
	 - Point to another MenuPath (such as "learning path for this topic").
3. **Inside a Document** (for example, a JSON quiz), you can design buttons like "Next question" or "Next step" to guide learners forward.

As long as you follow these rules:

- MenuPath JSON describes a map with `id`, `title`, and `items`.
- Category JSON describes a topic list with `id`, `title`, and `items`.
- Whenever an item should be clickable, give it a `pointTo` with correct `type`, `data`, and `dataLocation`.

Then the whole site can grow like a **knowledge map**, extending endlessly. You do not need to know how to code to keep adding new learning paths and content.
