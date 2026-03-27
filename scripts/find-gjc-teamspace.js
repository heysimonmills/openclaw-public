#!/usr/bin/env node
/**
 * Find Good Jelly Co Teamspace in GSG workspace
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

async function main() {
    console.log('=== Finding Good Jelly Co Teamspace ===\n');
    
    // Search for Good Jelly content
    const searchResults = await notionRequest('/search', GSG_TOKEN, {
        method: 'POST',
        body: { 
            query: 'Good Jelly',
            page_size: 20
        }
    });
    
    console.log(`Found ${searchResults.results.length} results:\n`);
    
    for (const result of searchResults.results) {
        const title = result.title?.[0]?.plain_text 
            || result.properties?.title?.title?.[0]?.plain_text
            || result.properties?.Name?.title?.[0]?.plain_text
            || 'Untitled';
        
        console.log(`${result.object.toUpperCase()}: ${title}`);
        console.log(`  ID: ${result.id}`);
        
        if (result.parent) {
            console.log(`  Parent type: ${result.parent.type}`);
        }
        
        // Check if this is a teamspace
        if (result.object === 'page' && result.parent?.type === 'workspace') {
            console.log(`  ⚠️  This is a top-level page (potential teamspace root)`);
        }
        
        console.log('');
    }
}

main().catch(console.error);
