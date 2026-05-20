const { Plugin, Notice } = require('obsidian');

module.exports = class CensorTool extends Plugin {
  async onload() {
    this.addCommand({
      id: 'toggle-censor',
      name: 'Toggle censor on selection',
      editorCallback: (editor) => {
        const selected = editor.getSelection();
        if (!selected) {
          new Notice('No text selected!');
          return;
        }

        // If already censored, uncensor it
        if (selected.startsWith('%%CENSOR%%') && selected.endsWith('%%/CENSOR%%')) {
          const inner = selected.slice('%%CENSOR%%'.length, -'%%/CENSOR%%'.length);
          editor.replaceSelection(inner);
          new Notice('🔓 Censor removed');
          return;
        }

        // Otherwise wrap it
        editor.replaceSelection(`%%CENSOR%%${selected}%%/CENSOR%%`);
        new Notice('🔒 Text censored');
      }
    });
  }
}