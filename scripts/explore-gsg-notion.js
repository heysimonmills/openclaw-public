#!/usr/bin/env node
/**
 * Explore GSG (George St Growth) Notion Workspace
 * Uses the config token to list target databases
 */

const GSG_TOKEN = 'YOUR_NOTION_API_TOKEN';

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

async function main() {
    console.log('=== Exploring GSG Workspace ===\n');
    
    try {
        // Get all searchable content
        const allResults = await searchWorkspace(GSG_TOKEN);
        
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
            console.log(`   URL: ${db.url}`);
        }
        
        console.log(`\n\n📄 TOP PAGES (${Math.min(pages.length, 20)}):`);
        console.log('=' .repeat(50));
        
        for (const page of pages.slice(0, 20)) {
            const title = page.properties?.title?.title?.[0]?.plain_text 
                || page.properties?.Name?.title?.[0]?.plain_text
                || 'Untitled';
            console.log(`   ${title} (${page.id})`);
        }
        
        // Check for GJC related content
        const gjcContent = allResults.filter(r => {
            const title = r.title?.[0]?.plain_text 
                || r.properties?.title?.title?.[0]?.plain_text 
                || r.properties?.Name?.title?.[0]?.plain_text
                || '';
            return title.toLowerCase().includes('good jelly') || title.toLowerCase().includes('gjc');
        });
        
        console.log(`\n\n🍯 GJC-Related Content Found (${gjcContent.length}):`);
        console.log('=' .repeat(50));
        for (const item of gjcContent) {
            const title = item.title?.[0]?.plain_text 
                || item.properties?.title?.title?.[0]?.plain_text
                || item.properties?.Name?.title?.[0]?.plain_text
                || 'Untitled';
            console.log(`   ${item.object.toUpperCase()}: ${title} (${item.id})`);
        }
        
    } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
    }
}

main();
