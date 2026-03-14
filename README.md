# [句句韺 JuJuEn](https://jujuen.org/)
Every sentence with pinyin/zhuyin and English.

- 專給需要同時學習中文／英文的大小朋友之網站，用學校各科考題和中國古書，並提供拼音、注音和英文，讓你一邊閱讀或做題目，一邊把漢字的長相、讀音和英文意思記起來。

- 专给需要同时学习中文／英文的大小朋友之网站，用学校各科考题和中国古书，并提供拼音、注音和英文，让你一边阅读或做题目，一边把汉字的长相、读音和英文意思记起来。

- A website specially designed for learners of all ages who need to study Chinese and English at the same time. It uses school exam questions from various subjects and classic Chinese books, and provides pinyin, zhuyin, and English so that you can read or work on questions while memorizing the appearance, pronunciation, and English meaning of Chinese characters.

## 分支 Branches

- [國中科目 Junior High Subjects](https://jujuen.org/junior-high)
- [中國古書 Ancient Chinese Classics](https://jujuen.org/ancient-classics)

## 如何自建分支 How to build your own branch

- 查看["自建知識"](https://jujuen.org/self-built-knowledge)分支中的[How to build your own knowledge branch / 如何建立自己的知識分支]

- 要求 Copilot AI 依照 site-components.md 的 MenuPath 格式來建立 menu-path.json, 項目關係可利用以下方式表達來快速建立:

  * A -> B -> C
  * B -> B1
  * B -> B2
  * A: pointTo is type: "document", data: "github/md", dataLocation: "https://github.com/.../xxx.md" (it can be any GitHub location)
  * B: pointTo is type: "category", data: "github/json", dataLocation: "https://github.com/.../xxx.json" (it can be any GitHub location)
  * B1: pointTo is type: "document", data: "web/page", dataLocation: "any_web_url"
  * B2: pointTo is type: "document", data: "youtube", dataLocation: "any_youtube_url"
  * C: pointTo is type: "document", data: "notion", dataLocation: "ayny_notion_embedded_url"
 
- Https://JuJuEn.org/{Your_Branch}

One your branch has menu-path.json, then your banch can be presented by this url rule: Https://JuJuEn.org/Your_Branch
