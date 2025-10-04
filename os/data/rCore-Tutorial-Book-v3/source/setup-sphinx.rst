修改和構建本項目
====================================

.. toctree::
   :hidden:
   :maxdepth: 4
   
1. 參考 `這裡 <https://www.sphinx-doc.org/en/master/usage/installation.html>`_ 安裝 Sphinx。
2. 切換到倉庫目錄下， ``pip install -r requirements.txt`` 安裝各種 python 庫依賴。
3. :doc:`/rest-example` 是 ReST 的一些基本語法，也可以參考已完成的文檔。
4. 修改之後，在項目根目錄下 ``make clean && make html`` 即可在 ``build/html/index.html`` 查看本地構建的主頁。請注意在修改章節目錄結構或者更新各種配置文件/python 腳本之後需要 ``make clean`` 一下，不然可能無法正常更新。
5. 如想對項目做貢獻的話，直接提交 pull request 即可。

.. note:: 
   
   **實時顯示修改rst文件後的html文檔的方法**

   1. ``pip install autoload`` 安裝 Sphinx 自動加載插件。
   2. 在項目根目錄下 ``sphinx-autobuild source  build/html`` 即可在瀏覽器中訪問 `http://127.0.0.1:8000/` 查看本地構建的主頁。

.. note::

   **如何生成教程pdf電子版**

   注意：經過嘗試在 wsl 環境下無法生成 pdf ，請使用原生的 Ubuntu Desktop 或者虛擬機。

   1. 首先 ``sudo apt update`` ，然後通過 ``sudo apt install`` 安裝如下軟件包： latexmk texlive-latex-recommended texlive-latex-extra texlive-xetex fonts-freefont-otf texlive-fonts-recommended texlive-lang-chinese tex-gyre.
   2. 從 Node.js 官方網站下載最新版的 Node.js ，配置好環境變量並通過 ``npm --version`` 確認配置正確。然後通過 ``npm install -g @mermaid-js/mermaid-cli`` 安裝 mermaid 命令行工具。
   3. 確認 Python 環境配置正確，也即 ``make html`` 可以正常生成 html 。
   4. 打上必要的補丁：在根目錄下執行 ``git apply --reject scripts/latexpdf.patch`` 。
   5. 構建：在根目錄下執行 ``make latexpdf`` ，過程中會有很多 latex 的警告，但可以忽略。
   6. 構建結束後，電子版 pdf 可以在 ``build/latex/rcore-tutorial-book-v3.pdf`` 找到。

.. note::

   **如何生成epub格式**

   1. 配置好 Sphinx Python 環境。
   2. ``make epub`` 構建 epub 格式輸出，產物可以在 ``build/epub/rCore-Tutorial-Book-v3.epub`` 中找到。