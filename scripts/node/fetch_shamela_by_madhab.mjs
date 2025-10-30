#!/usr/bin/env node
/**
 * Shamela Fiqh Downloader (Multi‑Madhab)
 *
 * Downloads books for a given fiqh school (maliki | hanafi | shafii | hanbali)
 * from the Shamela master database via the `shamela` package. Attempts to use
 * category matching by Arabic names; falls back to authoritative book name
 * patterns if category mapping is unavailable.
 *
 * Usage:
 *   node scripts/node/fetch_shamela_by_madhab.mjs --madhab=hanafi [--limit=50]
 */

import { configure, getMaster, downloadBook } from 'shamela';
import { writeFile, mkdir } from 'fs/promises';
import { join } from 'path';

// CLI args
const args = Object.fromEntries(
  process.argv.slice(2).map((arg) => {
    const [k, v] = arg.replace(/^--/, '').split('=');
    return [k, v ?? 'true'];
  })
);

const MADHAB = (args.madhab || 'maliki').toLowerCase();
const LIMIT = args.limit ? parseInt(args.limit, 10) : undefined;

if (!['maliki', 'hanafi', 'shafii', 'hanbali'].includes(MADHAB)) {
  console.error("❌ Invalid --madhab. Use one of: maliki|hanafi|shafii|hanbali");
  process.exit(1);
}

const OUTPUT_DIR = `data/shamela/raw/${MADHAB}`;
const METADATA_FILE = `data/shamela/${MADHAB}_metadata.json`;

// Shamela API endpoints
const SHAMELA_API_KEY = process.env.SHAMELA_API_KEY || '';
const SHAMELA_BOOKS_ENDPOINT = 'https://app.turath.io/api/books';
const SHAMELA_MASTER_ENDPOINT = 'https://app.turath.io/api/master_patch';

function configureShamela() {
  console.log('🔧 Configuring Shamela API client...');
  const config = {
    apiKey: SHAMELA_API_KEY || 'placeholder-key',
    booksEndpoint: SHAMELA_BOOKS_ENDPOINT,
    masterPatchEndpoint: SHAMELA_MASTER_ENDPOINT,
  };
  configure(config);
  console.log('✅ Shamela client configured\n');
}

function getArabicCategoryLabel(key) {
  switch (key) {
    case 'maliki': return 'الفقه المالكي';
    case 'hanafi': return 'الفقه الحنفي';
    case 'shafii': return 'الفقه الشافعي';
    case 'hanbali': return 'الفقه الحنبلي';
    default: return '';
  }
}

function getNamePatterns(key) {
  const map = {
    maliki: ['المالكي', 'المدونة', 'الرسالة', 'مختصر خليل', 'الموطأ'],
    hanafi: ['الحنفي', 'الهداية', 'بدائع الصنائع', 'رد المحتار', 'ابن عابدين', 'فقه حنفي'],
    shafii: ['الشافعي', 'الأم', 'المجموع', 'منهاج الطالبين', 'روضة الطالبين', 'فقه شافعي'],
    hanbali: ['الحنبلي', 'المغني', 'زاد المستقنع', 'الإنصاف', 'كشاف القناع', 'فقه حنبلي'],
  };
  return map[key] || [];
}

function tryResolveCategories(master, key) {
  const label = getArabicCategoryLabel(key);
  const containers = [master.categories, master.cats, master.categoriesMap, master.subjects];
  const ids = new Set();
  for (const container of containers) {
    if (!container) continue;
    // container may be array or object
    if (Array.isArray(container)) {
      for (const c of container) {
        const name = (c.name || c.title || '').toString();
        const id = c.id ?? c.cat ?? c._id;
        if (name.includes(label)) ids.add(id);
      }
    } else {
      for (const [id, value] of Object.entries(container)) {
        const name = (value && (value.name || value.title || value)).toString();
        if (name.includes(label)) ids.add(parseInt(id, 10));
      }
    }
  }
  return Array.from(ids).filter(Boolean);
}

function selectBooksByMadhab(master, key) {
  // 1) Prefer categories by Arabic label
  const catIds = tryResolveCategories(master, key);
  if (catIds.length > 0) {
    const books = master.books.filter((b) => catIds.includes(b.cat));
    if (books.length > 0) return books;
  }

  // 2) Fallback to well-known book name patterns
  const patterns = getNamePatterns(key);
  if (patterns.length > 0) {
    const books = master.books.filter((b) => {
      const name = (b.name || '').toString();
      return patterns.some((p) => name.includes(p));
    });
    if (books.length > 0) return books;
  }

  // 3) As last resort, filter by including madhab arabic keyword in name
  const keyword = getArabicCategoryLabel(key).replace('الفقه ', '').trim();
  const fallback = master.books.filter((b) => (b.name || '').toString().includes(keyword));
  return fallback;
}

async function downloadSingleBook(bookId, bookName, index, total) {
  const outputPath = join(OUTPUT_DIR, `${bookId}.json`);
  try {
    console.log(`[${index}/${total}] 📖 Downloading: ${bookName} (ID: ${bookId})`);
    await downloadBook(bookId, { outputFile: { path: outputPath } });
    console.log(`    ✅ Saved to ${outputPath}`);
    return { success: true, bookId, path: outputPath };
  } catch (error) {
    console.error(`    ❌ Failed to download book ${bookId}: ${error.message}`);
    return { success: false, bookId, error: error.message };
  }
}

async function main() {
  try {
    console.log('\n' + '='.repeat(70));
    console.log(`🕌 SHAMELA ${MADHAB.toUpperCase()} FIQH DOWNLOADER`);
    console.log('='.repeat(70) + '\n');

    // Step 1: Configure client
    configureShamela();

    // Step 2: Load master
    console.log('📥 Fetching master database...');
    const master = await getMaster();
    console.log(`✅ Master DB loaded: ${master.books.length} total books\n`);

    // Step 3: Select books for madhab
    let books = selectBooksByMadhab(master, MADHAB);
    if (LIMIT && Number.isFinite(LIMIT)) {
      books = books.slice(0, LIMIT);
    }

    console.log(`📚 Selected ${books.length} ${MADHAB} books`);

    // Save metadata
    await mkdir('data/shamela', { recursive: true });
    await mkdir(OUTPUT_DIR, { recursive: true });
    await writeFile(
      METADATA_FILE,
      JSON.stringify(
        {
          madhab: MADHAB,
          total_books: books.length,
          fetched_at: new Date().toISOString(),
          books: books.map((b) => ({ id: b.id, name: b.name, author_id: b.auth_id, cat: b.cat })),
        },
        null,
        2
      ),
      'utf-8'
    );
    console.log(`✅ Saved metadata to ${METADATA_FILE}`);

    // Step 4: Download all
    const results = [];
    const total = books.length;
    for (let i = 0; i < books.length; i++) {
      const b = books[i];
      const r = await downloadSingleBook(b.id, b.name, i + 1, total);
      results.push(r);
      if (i < books.length - 1) {
        await new Promise((res) => setTimeout(res, 2000));
      }
    }

    // Summary
    const ok = results.filter((r) => r.success).length;
    const bad = results.length - ok;
    console.log('\n' + '='.repeat(70));
    console.log('📊 DOWNLOAD SUMMARY');
    console.log('='.repeat(70));
    console.log(`✅ Successful: ${ok}`);
    console.log(`❌ Failed: ${bad}`);
    console.log(`📦 Total: ${results.length}`);
    console.log('\n'.repeat(1));
    console.log('✨ Next steps:');
    console.log('  1) Convert to chunks: python scripts/shamela_converter.py (or a multi-madhab converter)');
    console.log('  2) Ingest into Qdrant with madhab tagging using a conversion pipeline');
    console.log('='.repeat(70));
    process.exit(0);
  } catch (err) {
    console.error('\n❌ Fatal error:', err);
    process.exit(1);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}


