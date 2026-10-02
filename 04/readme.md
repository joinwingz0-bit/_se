以下是這四個核心概念在 **Git 指令**、**GitHub 網頁操作** 以及 **核心觀念** 上的重點整理：

---

### 1. 分支（Branch）

* **核心觀念**：從現有的開發主線（如 `main`）分流出來的獨立工作區。在新功能開發或修復錯誤時使用，避免尚未穩定的程式碼影響主線。
* **常用指令**：
```bash
# 建立並切換至新分支
git checkout -b <分支名稱>
# （現代 Git 推薦語法）
git switch -c <分支名稱>

# 查看本地所有分支
git branch

# 將新分支推送到 GitHub 遠端
git push -u origin <分支名稱>

```


* **GitHub 網頁操作**：
* 在儲存庫首頁左上角的分支選單（預設顯示 `main`），點開後在輸入框輸入新分支名稱，點擊「Create branch: ...」即可直接從網頁建立。



---

### 2. 合併（Merge）

* **核心觀念**：將某個分支上完成並測試無誤的提交（commits），整合回目標分支（例如將 `developGitBranch` 合併回 `main`）。
* **常用指令**：
```bash
# 1. 先切換至要接收變更的目標分支（通常是 main）
git checkout main   # 或 git switch main

# 2. 將開發分支合併進來
git merge <分支名稱>

# 3. 將合併後的成果推送到遠端
git push origin main

```


* **常見情況**：
* **Fast-forward**：主分支期間沒有其他提交，Git 直接將指標往前移動。
* **Conflict（衝突）**：兩邊修改到同一檔案的相同行數，需手動挑選保留內容、重新 `git add .` 與 `git commit`。



---

### 3. Fork

* **核心觀念**：這是 **GitHub 提供的服務機制**（Git 指令本身沒有 `fork` 指令）。當你對某個專案（母專案）沒有直接推送（Push）權限時，可以複製一份完整的專案到自己的 GitHub 帳號底下（子專案），在自己的地盤自由修改。
* **操作步驟**：
1. **GitHub 網頁操作**：
* 前往母專案頁面（例如 `[https://github.com/se-test-example/git-examples](https://github.com/se-test-example/git-examples)`）。
* 點擊右上角的 **Fork** 按鈕，選擇建立到你的個人帳號（例如 `[https://github.com/joinwingz0-bit/git-examples](https://github.com/joinwingz0-bit/git-examples)`）。


2. **本地端配合指令**：
```bash
# Clone 自己帳號下的子專案到本機
git clone https://github.com/<你的帳號>/git-examples.git
cd git-examples

# 新增或修改檔案後提交並推送回自己的儲存庫
git add .
git commit -m "add new feature"
git push origin main

```





---

### 4. Pull Request (PR)

* **核心觀念**：向專案擁有者發出「代碼審查與合併請求」。它告訴對方：「我寫好了一些功能/修復，請審核並考慮把它合併（Pull）進你的專案中」。
* **常見兩種情境**：
1. **同儲存庫分支間**：功能分支 `feature-x` 請求合併進主分支 `main`（**GitHub Flow**）。
2. **跨儲存庫（跨 Fork）**：個人子專案請求合併回上游母專案（**Forking Workflow**）。


* **GitHub 網頁操作步驟**：
1. 前往自己已推送變更的儲存庫頁面。
2. 點擊上方的 **Contribute** $\rightarrow$ **Open pull request**（或黃色橫條的 **Compare & pull request**）。
3. **設定比對方向**：
* **base repository / branch**（目標）：母專案的主分支（如 `se-test-example/git-examples` 的 `main`）。
* **head repository / compare**（來源）：你的子專案或功能分支（如 `joinwingz0-bit/git-examples`）。


4. 檢查下方 Diff 變更內容確認無誤。
5. 填寫標題與變更說明，點擊 **Create pull request** 送出等待審查。          