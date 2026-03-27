#!/usr/bin/env node
/**
 * Explore Good Jelly Co Notion Workspace
 * Uses the provided integration secret to list all databases and pages
 */

const GJC_TOKEN = 'YOUR_NOTION_API_TOKEN';

async function notionRequest(endpoint, token, options = {}) {
    const url = `https://api.notion.com/v1${endpoint}`;
    const response = await fetch(url, {
        method: options.method || 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json',
            ...options.headers
        },
        body: options.body ? JSON.stringify(options.body) : undefined
    });
    
    if (!response.ok) {
        const error = await response.text();
        throw new Error(`Notion API error: ${response.status} - ${error}`);
    }
    
    return response.json();
}

async function searchWorkspace(token, query = '') {
    const results = [];
    let cursor = undefined;
    
    do {
        const body = {
            query,
            page_size: 100
        };
        if (cursor) body.start_cursor = cursor;
        
        const response = await notionRequest('/search', token, {
            method: 'POST',
            body
        });
        
        results.push(...response.results);
        cursor = response.next_cursor;
        
    } while (cursor);
    
    return results;
}

async function getDatabaseSchema(token, databaseId) {
    return await notionRequest(`/databases/${databaseId}`, token);
}

async function getDatabaseEntries(token, databaseId) {
    const entries = [];
    let cursor = undefined;
    
    do {
        const body = { page_size: 100 };
        if (cursor) body.start_cursor = cursor;
        
        const response = await notionRequest(`/databases/${databaseId}/query`, token, {
            method: 'POST',
            body
        });
        
        entries.push(...response.results);
        cursor = response.next_cursor;
        
    } while (cursor);
    
    return entries;
}

async function getPageContent(token, pageId) {
    return await notionRequest(`/blocks/${pageId}/children`, token);
}

async function main() {
    console.log('=== Exploring Good Jelly Co Workspace ===\n');
    
    try {
        // Get all searchable content
        const allResults = await searchWorkspace(GJC_TOKEN);
        
        console.log(`Found ${allResults.length} total items:\n`);
        
        // Separate by type
        const databases = allResults.filter(r => r.object === 'database');
        const pages = allResults.filter(r => r.object === 'page');
        
        console.log(`📊 DATABASES (${databases.length}):`);
        console.log('=' .repeat(50));
        
        for (const db of databases) {
            const title = db.title?.[0]?.plain_text || 'Untitled';
            const props = Object.keys(db.properties || {}).join(', ');
            console.log(`\n📁 ${title}`);
            console.log(`   ID: ${db.id}`);
            console.log(`   Properties: ${props || 'none'}`);
            
            // Get entry count
            try {
                const entries = await getDatabaseEntries(GJC_TOKEN, db.id);
                console.log(`   Entries: ${entries.length}`);
            } catch (e) {
                console.log(`   Entries: (could not query - ${e.message})`);
            }
        }
        
        console.log(`\n\n📄 PAGES (${pages.length}):`);
        console.log('=' .repeat(50));
        
        for (const page of pages.slice(0, 50)) { // Limit output
            const title = page.properties?.title?.title?.[0]?.plain_text 
                || page.properties?.Name?.title?.[0]?.plain_text
                || 'Untitled';
            console.log(`\n📝 ${title}`);
            console.log(`   ID: ${page.id}`);
            console.log(`   Parent: ${page.parent?.type || 'unknown'}`);
            
            // Get page content summary
            try {
                const content = await getPageContent(GJC_TOKEN, page.id);
                const blockCount = content.results?.length || 0;
                console.log(`   Content blocks: ${blockCount}`);
            } catch (e) {
                console.log(`   Content: (could not fetch - ${e.message})`);
            }
        }
        
        if (pages.length > 50) {
            console.log(`\n... and ${pages.length - 50} more pages`);
        }
        
        // Export full structure for migration
        const exportData = {
            databases: databases.map(db => ({
                id: db.id,
                title: db.title?.[0]?.plain_text || 'Untitled',
                properties: db.properties,
                url: db.url
            })),
            pages: pages.map(p => ({
                id: p.id,
                title: p.properties?.title?.title?.[0]?.plain_text 
                    || p.properties?.Name?.title?.[0]?.plain_text
                    || 'Untitled',
                parent: p.parent,
                url: p.url
            }))
        };
        
        console.log('\n\n=== Export Summary ===');
        console.log(JSON.stringify(exportData, null, 2));
        
    } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
    }
}

main();
