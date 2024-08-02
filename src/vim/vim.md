# VIM

## NVIM 編譯

```sh
# 關閉  anaconda 因為編譯環境會導向 anaconda lib
conda deactivate  

sudo apt-get install ninja-build \
     gettext libtool libtool-bin \
     autoconf automake cmake g++ \
     pkg-config unzip xsel

git clone https://github.com/neovim/neovim.git
cd neovim
git checkout stable
make CMAKE_EXTRA_FLAGS="-DCMAKE_INSTALL_PREFIX=$HOME/.mybin/nvim" CMAKE_BUILD_TYPE=Release  -j8
make install

cd ~/.mybin/nvim/share/nvim/runtime/autoload
wget https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim

# copy vimrc to /home/shihyu/.config/nvim/init.vim   
 /home/shihyu/.config/nvim/init.vim
 
 
No "python3" provider found. Run :checkhealth provider
pip install --user --upgrade pynvim


# node 要新版的不然 coc 會報錯
sudo n 16 

// Enable Copy and Paste 
sudo apt-get install xclip xsel
```

```sh
CocInstall coc-rust-analyzer coc-tabnine coc-clangd coc-cmake coc-css coc-html coc-json coc-r-lsp coc-go coc-pyright coc-tsserver coc-sh coc-rls
```

Inlay Hints默認是打開的，下次打開vim還會啟用，永久關閉可以在coc-nvim的組態檔案裡修改。
vim裡執行`:CocConfig`打開coc的組態檔案，新增：

```json
{
    "inlayHint.enable":false
}
```

- ~/.config/nvim/coc-settings.json

```sh
{
// 要空
}
```

```sh
clangd.path 要空的
CocInstall coc-clangd
CocCommand clangd.install

CocInstall coc-go
CocCommand go.install.gopls

CocInstall coc-pyright
CocInstall coc-json coc-tsserver
```

````sh
# neovim
## Config (`.config/nvim/init.vim`)
```
" Neovim vimrc 

"filetype plugin indent on    " required

" Use Vim settings rather than Vi settings
set nocompatible

" Make backspace normal
set backspace=indent,eol,start

" Syntax highlighting
syntax on
filetype plugin on

" Show line numbers
set number

" Allow hidden buffers, don't limit 1 file per window/split
set hidden

" Set default Vim terminal window size to account for line number spacing
" set lines=24 columns=82

" Swaps, Undo, Backups
set undodir=~/.vim/undo/
set backupdir=~/.vim/backups/
set directory=~/.vim/swaps/
" Added 12/14/2017
set backup
set undofile
set swapfile
" Source .vimrc if present in working directory
set exrc

" Restrict usage of write/execution shell commands
set secure

" Search down into subfolders and provide tab-completion for file-tasks
set path+=**
set tabstop=4
set shiftwidth=4
set expandtab
" Attempt to fix tmux/gnome-terminal color differences in Vim
set background=dark

" Set default color 
colorscheme slate

" Alter line numbers and background
hi Normal ctermbg=none
hi LineNr ctermfg=blue

" Add a color column at max line len
hi ColorColumn ctermbg=darkgrey

" Try and fix netrw:
" Make smaller and rid banner
" from here: https://shapeshed.com/vim-netrw/
let g:netrw_banner = 0
let g:netrw_winsize = 25

let g:vim_jsx_pretty_colorful_config = 1 " default 0
" python path
"
let g:python3_host_prog="/usr/bin/python3"
" Set neovim's clipboard 
" https://github.com/neovim/neovim/wiki/FAQ#how-to-use-the-windows-clipboard-from-wsl
set clipboard=unnamedplus

call plug#begin()
Plug 'neoclide/coc.nvim', {'branch': 'release'}
Plug 'HerringtonDarkholme/yats.vim'
Plug 'yuezk/vim-js'
Plug 'maxmellon/vim-jsx-pretty'
if has('nvim')
  Plug 'Shougo/denite.nvim', { 'do': ':UpdateRemotePlugins' }
else
  Plug 'Shougo/denite.nvim'
  Plug 'roxma/nvim-yarp'
  Plug 'roxma/vim-hug-neovim-rpc'
endif
call plug#end()

" === Denite setup ==="
" Use ripgrep for searching current directory for files
" By default, ripgrep will respect rules in .gitignore
"   --files: Print each file that would be searched (but don't search)
"   --glob:  Include or exclues files for searching that match the given glob
"            (aka ignore .git files)
"
call denite#custom#var('file/rec', 'command', ['rg', '--files', '--glob', '!.git'])

" Use ripgrep in place of "grep"
call denite#custom#var('grep', 'command', ['rg'])

" Custom options for ripgrep
"   --vimgrep:  Show results with every match on it's own line
"   --hidden:   Search hidden directories and files
"   --heading:  Show the file name above clusters of matches from each file
"   --S:        Search case insensitively if the pattern is all lowercase
call denite#custom#var('grep', 'default_opts', ['--hidden', '--vimgrep', '--heading', '-S'])

" Recommended defaults for ripgrep via Denite docs
call denite#custom#var('grep', 'recursive_opts', [])
call denite#custom#var('grep', 'pattern_opt', ['--regexp'])
call denite#custom#var('grep', 'separator', ['--'])
call denite#custom#var('grep', 'final_opts', [])

" Remove date from buffer list
call denite#custom#var('buffer', 'date_format', '')

" Custom options for Denite
"   auto_resize             - Auto resize the Denite window height automatically.
"   prompt                  - Customize denite prompt
"   direction               - Specify Denite window direction as directly below current pane
"   winminheight            - Specify min height for Denite window
"   highlight_mode_insert   - Specify h1-CursorLine in insert mode
"   prompt_highlight        - Specify color of prompt
"   highlight_matched_char  - Matched characters highlight
"   highlight_matched_range - matched range highlight
let s:denite_options = {'default' : {
\ 'split': 'floating',
\ 'start_filter': 1,
\ 'auto_resize': 1,
\ 'source_names': 'short',
\ 'prompt': 'λ ',
\ 'highlight_matched_char': 'QuickFixLine',
\ 'highlight_matched_range': 'Visual',
\ 'highlight_window_background': 'Visual',
\ 'highlight_filter_background': 'DiffAdd',
\ 'winrow': 1,
\ 'vertical_preview': 1
\ }}

" Loop through denite options and enable them
function! s:profile(opts) abort
  for l:fname in keys(a:opts)
    for l:dopt in keys(a:opts[l:fname])
      call denite#custom#option(l:fname, l:dopt, a:opts[l:fname][l:dopt])
    endfor
  endfor
endfunction

call s:profile(s:denite_options)

" Special filetype settings
autocmd FileType html setlocal shiftwidth=2 tabstop=2
autocmd FileType javascript setlocal shiftwidth=2 tabstop=2
autocmd FileType css setlocal shiftwidth=2 tabstop=2
autocmd FileType jsx setlocal shiftwidth=2 tabstop=2
autocmd FileType tsx setlocal shiftwidth=2 tabstop=2
autocmd FileType ts setlocal shiftwidth=2 tabstop=2
autocmd FileType py setlocal shiftwidth=4 tabstop=4
```
## Setup
### Plugin system [`vim-plug`](https://github.com/junegunn/vim-plug)
```
sh -c 'curl -fLo "${XDG_DATA_HOME:-$HOME/.local/share}"/nvim/site/autoload/plug.vim --create-dirs \
       https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim'
```
### Language servers
- `JavaScript`: https://github.com/neoclide/coc-tsserver `:CocInstall coc-tsserver`

- `Python`: https://github.com/neoclide/coc.nvim/wiki/Language-servers#python `:CocInstall coc-python`

- `bash`: https://github.com/josa42/coc-sh `:CocInstall coc-sh`

- `C/C++`: 
RHEL8: 
```
sudo dnf install clang
```

Ubuntu:
```
sudo apt install clangd-10 # as of fall 2020
```
In vim/neovim:
```
:CocInstall coc-clangd
```
- `cmake`: `:CocInstall coc-cmake`
- `css`: `:CocInstall coc-css`
- `html`: `:CocInstall coc-html`
- `json`: `:CocInstall coc-json`
- `R`: `:CocInstall coc-r-lsp`
- `go`: `:CocInstall coc-go`
- `python`: `:CocInstall coc-pyright`

Do a bunch, all in one go, e.g. `:CocInstall coc-tabnine coc-clangd coc-cmake coc-css coc-html coc-json coc-r-lsp coc-go coc-pyright coc-tsserver coc-sh coc-rls`!

### Tabnine Pro Key
If you're a user of [TabNine](https:://www.TabNine.com) within multiple editing environments, you probably have a pro key. As [coc-tabnine](https://github.com/neoclide/coc-tabnine) is community supported, you'll need to use the `TabNine::config` **Magic String** to configure your key in settings.
````



