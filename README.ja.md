# Build script for iOS project.
iOSプロジェクト用のビルドスクリプトです。

# 使いかた
iOSプロジェクト直下にpuild.pyファイルを置き、実行します。

    $ build.py [-t NAME] [-c NAME]

    -t --target ビルドするTarget名を指定します。省略時の値はソースのDEFAULT_TARGETSに定義します
    -c --configuration ビルドするConfiguration名を指定します。省略時の値はソースのDEFAULT_CONFIGURATIONSに定義します

完了すると、.ipaファイルが build/\<target.name\>_\<configuration.name\>_\<versionName\>.\<versionCode\>.ipa に出力されます。

Configurationが'Release'であれば、AppStore向けのzipファイルを出力します。

尚、事前準備として、ソース40行目付近のINFO_PLIST_FILE_PATH, COPYRIGHT_FILE_PATH, DEFAULT_TARGETS, DEFAULT_CONFIGURATIONSをプロジェクトに合わせて変更してください。


# スクリプトの処理内容
本スクリプトは、以下の処理を行ないます。

1. ビルド前にInfo.plistを更新します

    1.1 CFBundleVersionをインクリメント

1. copyright.plistを生成もしくは更新します

1. xcodebuildによるビルドを実行します

1. .ipa/zipファイルを生成します（フォーマットは上記）



# 注意事項：スクリプトが自動生成するファイルについて

### build.version

ビルド時にインクリメントしたCFBundleVersionが格納され、次のビルドで使用されます。

ブランチを切り替えても常にCFBundleVersionが前に進むようにするために
VCSのignoreファイルに追加しておくことをおすすめします。


### copyright.plist

アプリ内でCopyright表示に使うための"年"が書きこまれます。

ただし、"copyright\_year\_to"の値が未来年の場合、値は上書きされません
（今年に戻されてしまうことはありません）。
