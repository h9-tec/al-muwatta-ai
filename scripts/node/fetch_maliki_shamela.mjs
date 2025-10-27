#!/usr/bin/env node
/**
 * Shamela Maliki Fiqh Downloader
 * 
 * Downloads all books from Shamela category 15 (الفقه المالكي) 
 * using the official Shamela API via the ragaeeb/shamela library.
 * 
 * Outputs JSON files to data/shamela/raw/ for Python ingestion.
 */

import { configure, getMaster, downloadBook } from 'shamela';
import { writeFile, mkdir } from 'fs/promises';
import { join } from 'path';

// Configuration
const MALIKI_CATEGORY_ID = 15;
const OUTPUT_DIR = 'data/shamela/raw';
const METADATA_FILE = 'data/shamela/maliki_metadata.json';

// Shamela API endpoints (v4)
// Using app.turath.io mirror which hosts Shamela API
const SHAMELA_API_KEY = process.env.SHAMELA_API_KEY || '';
const SHAMELA_BOOKS_ENDPOINT = 'https://app.turath.io/api/books';
const SHAMELA_MASTER_ENDPOINT = 'https://app.turath.io/api/master_patch';

/**
 * Configure the Shamela client with API endpoints
 */
function configureShamela() {
    console.log('🔧 Configuring Shamela API client...');
    
    // The shamela library REQUIRES apiKey even if the API doesn't
    // Use a placeholder if not provided
    const config = {
        apiKey: SHAMELA_API_KEY || 'placeholder-key',
        booksEndpoint: SHAMELA_BOOKS_ENDPOINT,
        masterPatchEndpoint: SHAMELA_MASTER_ENDPOINT,
    };
    
    configure(config);
    console.log('✅ Shamela client configured\n');
}

/**
 * Fetch all books from the Maliki fiqh category
 */
async function fetchMalikiBooks() {
    console.log('📥 Fetching master database...');
    const master = await getMaster();
    console.log(`✅ Master DB loaded: ${master.books.length} total books\n`);

    // Filter books by Maliki category
    const malikiBooks = master.books.filter(book => {
        // Check if book belongs to Maliki fiqh category (15)
        return book.cat === MALIKI_CATEGORY_ID;
    });

    console.log(`📚 Found ${malikiBooks.length} Maliki fiqh books\n`);

    // Save metadata for reference
    const metadata = {
        category_id: MALIKI_CATEGORY_ID,
        category_name: 'الفقه المالكي',
        total_books: malikiBooks.length,
        master_version: master.version,
        fetched_at: new Date().toISOString(),
        books: malikiBooks.map(book => ({
            id: book.id,
            name: book.name,
            author_id: book.auth_id,
            author_death: book.auth_death,
            category: book.cat,
        })),
    };

    await mkdir('data/shamela', { recursive: true });
    await writeFile(METADATA_FILE, JSON.stringify(metadata, null, 2), 'utf-8');
    console.log(`✅ Saved metadata to ${METADATA_FILE}\n`);

    return malikiBooks;
}

/**
 * Download a single book and save as JSON
 */
async function downloadSingleBook(bookId, bookName, index, total) {
    const outputPath = join(OUTPUT_DIR, `${bookId}.json`);
    
    try {
        console.log(`[${index}/${total}] 📖 Downloading: ${bookName} (ID: ${bookId})`);
        
        await downloadBook(bookId, {
            outputFile: { path: outputPath }
        });
        
        console.log(`    ✅ Saved to ${outputPath}`);
        return { success: true, bookId, path: outputPath };
        
    } catch (error) {
        console.error(`    ❌ Failed to download book ${bookId}: ${error.message}`);
        return { success: false, bookId, error: error.message };
    }
}

/**
 * Download all Maliki books with rate limiting
 */
async function downloadAllMalikiBooks(books) {
    console.log('=' .repeat(70));
    console.log('📥 DOWNLOADING MALIKI FIQH BOOKS');
    console.log('=' .repeat(70) + '\n');

    await mkdir(OUTPUT_DIR, { recursive: true });

    const results = [];
    const total = books.length;

    for (let i = 0; i < books.length; i++) {
        const book = books[i];
        const result = await downloadSingleBook(book.id, book.name, i + 1, total);
        results.push(result);

        // Rate limiting: wait 2 seconds between downloads
        if (i < books.length - 1) {
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
    }

    return results;
}

/**
 * Generate summary report
 */
function printSummary(results) {
    console.log('\n' + '=' .repeat(70));
    console.log('📊 DOWNLOAD SUMMARY');
    console.log('=' .repeat(70));

    const successful = results.filter(r => r.success);
    const failed = results.filter(r => !r.success);

    console.log(`\n✅ Successful: ${successful.length}`);
    console.log(`❌ Failed: ${failed.length}`);
    console.log(`📦 Total: ${results.length}\n`);

    if (failed.length > 0) {
        console.log('Failed downloads:');
        failed.forEach(f => {
            console.log(`   • Book ${f.bookId}: ${f.error}`);
        });
        console.log();
    }

    console.log('=' .repeat(70));
    console.log('✨ Next steps:');
    console.log('   1. Run: python scripts/shamela_converter.py');
    console.log('   2. Run: python scrape_and_populate_rag.py');
    console.log('   3. Restart backend: pkill -f uvicorn && uvicorn src.main:app --reload');
    console.log('=' .repeat(70) + '\n');
}

/**
 * Main execution
 */
async function main() {
    try {
        console.log('\n' + '=' .repeat(70));
        console.log('🕌 SHAMELA MALIKI FIQH DOWNLOADER');
        console.log('=' .repeat(70) + '\n');

        // Step 1: Configure client
        configureShamela();

        // Step 2: Fetch Maliki books list
        const malikiBooks = await fetchMalikiBooks();

        // Step 3: Download all books
        const results = await downloadAllMalikiBooks(malikiBooks);

        // Step 4: Print summary
        printSummary(results);

        process.exit(0);

    } catch (error) {
        console.error('\n❌ Fatal error:', error);
        process.exit(1);
    }
}

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
    main();
}

