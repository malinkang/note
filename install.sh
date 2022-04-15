
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
brew install autojump
#手动.zshrc配置zsh-autosuggestions zsh-syntax-highlighting
brew install zsh #zsh
brew install iterm2 #命令行工具
brew install fig
brew install p7zip 
#工具
brew install alfred
brew install raycast
brew install the-unarchiver #解压软件
brew install appcleaner #清理软件
brew install clashx #翻墙
brew install ticktick #滴答清单
brew install picgo #图床
brew install dropbox #网盘
brew install google-chrome #浏览器
#播放器
brew install iina 
brew install qqmusic 
brew install neteasemusic
#通讯
brew install telegram-desktop
brew install dingtalk 
brew install wechat
#开发工具
brew install rescuetime
brew install sogouinput
brew install visual-studio-code
brew install android-studio

brew install jadx
brew install scrcpy