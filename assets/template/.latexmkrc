# 在本目录运行 latexmk 即可编译；中间文件放 build/，成功后把 PDF 拷回本目录（阅读器打开它，会自动刷新）；编译组件库：latexmk components.tex
$pdf_mode = 1;
$out_dir = 'build';
@default_files = ('presentation.tex');
$success_cmd = 'cp %D .';   # 把 build/ 里的 PDF 拷回本目录（presentation.pdf / components.pdf）
$pdf_previewer = 'true';   # -pvc 持续模式下不自动打开阅读器
