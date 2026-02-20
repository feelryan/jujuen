1. https://fonts.google.com/icons

2. filter by category

3. mouse scroll down to the page bottom to have all icons on the page

4. paste the below code on the console

```
// Get all icon names from the current view
const icons = Array.from(document.querySelectorAll('.icon-name'))
  .map(el => el.textContent.trim().replaceAll(' ', '_'));
```
