<%*
const file = tp.file.find_tfile(tp.file.path(true));
const cache = app.metadataCache.getFileCache(file);
const fm = cache?.frontmatter;
const currentValue = fm?.publish;

if (currentValue === true) {
    await app.fileManager.processFrontMatter(file, (fm) => {
        fm["publish"] = false;
    });
    new Notice("🔒 Page unpublished");
} else {
    await app.fileManager.processFrontMatter(file, (fm) => {
        fm["publish"] = true;
    });
    new Notice("🌐 Page published!");
}
%>