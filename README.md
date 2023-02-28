# The purpose of this repositry
このレジストリは総合内科のオンコール表作成のためのレポジトリです。
git管理しています。混乱した時のgit pull --force的な呪文は以下の通りです 


git fetch origin main  

git reset --hard origin/main


  
# How to decide shift?

基本的なルールとして
- 絶対に、各自が-1にした日には入れない
- 平日は教育・病棟当直、土日祝日はA/B当直と一致していたらそこに優先的に入れる。
- 同日が両方とも総合内科の場合はランダムに決める。
- 土日祝日の夕方のオンコールは2回分の重み付け。
- 可能なら年間を通して、土日祝日午後とそれ以外の回数が一定になるようにする。

# How to use this script?

csv fileは手動で変更が必要です。
病院の当直が決まったら、それを元に入れてください。person 1, 2となっています。

