const pptxgen = require('pptxgenjs');
const path = require('path');
const html2pptx = require('/Users/jaapbranderhorst/.claude/plugins/cache/anthropic-agent-skills/document-skills/69c0b1a06741/skills/pptx/scripts/html2pptx.js');

async function build() {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  pptx.title = 'Turning Claude Code into a Software Factory';
  pptx.author = 'Jaap Branderhorst';

  const slidesDir = path.join(__dirname, 'workspace', 'slides');
  const slideFiles = [];
  for (let i = 1; i <= 12; i++) {
    slideFiles.push(path.join(slidesDir, `slide${String(i).padStart(2, '0')}.html`));
  }

  for (const slideFile of slideFiles) {
    console.log(`Processing: ${path.basename(slideFile)}`);
    try {
      const { slide, placeholders } = await html2pptx(slideFile, pptx);
      console.log(`  OK`);
    } catch (err) {
      console.error(`  ERROR: ${err.message}`);
    }
  }

  const outputPath = path.join(__dirname, 'presentation.pptx');
  await pptx.writeFile({ fileName: outputPath });
  console.log(`\nSaved: ${outputPath}`);
}

build().catch(err => {
  console.error('Build failed:', err);
  process.exit(1);
});
