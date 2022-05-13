# copilot

https://github.com/github/copilot.vim

1. Install [Node.js](https://nodejs.org/en/download/) 12 or newer.

2. Install [Neovim](https://github.com/neovim/neovim/releases/latest) 0.6 or newer.

3. Install `github/copilot.vim` using vim-plug, packer.nvim, or any other plugin manager. Or to install directly:

   - 手動更新

   ```sh
   git clone https://github.com/github/copilot.vim.git \
     ~/.config/nvim/pack/github/start/copilot.vim
   ```

4. Start Neovim and invoke `:Copilot setup`.

https://github.com/github/copilot.vim/blob/release/doc/copilot.txt

```sh
:Copilot disable        Globally disable GitHub Copilot inline suggestions.

                                                *:Copilot_enable*
:Copilot enable         Re-enable GitHub Copilot after :Copilot disable.

                                                *:Copilot_feedback*
:Copilot feedback       Open the website for providing GitHub Copilot
                        feedback.

                                                *:Copilot_setup*
:Copilot setup          Authenticate and enable GitHub Copilot.

                                                *:Copilot_signout*
:Copilot signout        Sign out of GitHub Copilot.

                                                *:Copilot_status*
:Copilot status         Check if GitHub Copilot is operational for the current
                        buffer and report on any issues.

                                                *:Copilot_panel*
:Copilot panel          Open a window with up to 10 completions for the
                        current buffer.  Use <CR> to accept a solution.  Maps
                        are also provided for [[ and ]] to jump from solution
                        to solution.  This is the default command if :Copilot
                        is called without an argument.
```

