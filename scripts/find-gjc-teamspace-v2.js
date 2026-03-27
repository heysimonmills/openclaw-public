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
    console.log('=== Searching for Good Jelly Co Teamspace ===\n');
    
    // Search for teamspace
    const searchResults = await notionRequest('/search', GSG_TOKEN, {
        method: 'POST',
        body: { 
            query: 'Good Jelly Co Teamspace',
            page_size: 20
        }
    });
    
    console.log(`Found ${searchResults.results.length} results for "Good Jelly Co Teamspace":\n`);
    
    for (const result of searchResults.results) {
        const title = result.title?.[0]?.plain_text 
            || result.properties?.title?.title?.[0]?.plain_text
            || result.properties?.Name?.title?.[0]?.plain_text
            || 'Untitled';
        
        console.log(`${result.object.toUpperCase()}: ${title}`);
        console.log(`  ID: ${result.id}`);
        console.log(`  Parent type: ${result.parent?.type}`);
        if (result.parent?.page_id) {
            console.log(`  Parent ID: ${result.parent.page_id}`);
        }
        console.log(`  URL: ${result.url}`);
        console.log('');
    }
    
    // Also search for just "teamspace" to find all teamspaces
    console.log('\n=== Searching for all teamspaces ===\n');
    
    const teamspaceResults = await notionRequest('/search', GSG_TOKEN, {
        method: 'POST',
        body: { 
            query: 'teamspace',
            page_size: 20
        }
    });
    
    for (const result of teamspaceResults.results) {
        const title = result.title?.[0]?.plain_text 
            || result.properties?.title?.title?.[0]?.plain_text
            || result.properties?.Name?.title?.[0]?.plain_text
            || 'Untitled';
        
        console.log(`${result.object.toUpperCase()}: ${title} (${result.id})`);
    }
    
    // Check all workspace-level pages
    console.log('\n=== All workspace-level pages ===\n');
    
    const allResults = await notionRequest('/search', GSG_TOKEN, {
        method: 'POST',
        body: { page_size: 100 }
    });
    
    const workspacePages = allResults.results.filter(r => 
        r.object === 'page' && r.parent?.type === 'workspace'
    );
    
    for (const page of workspacePages) {
        const title = page.properties?.title?.title?.[0]?.plain_text 
            || 'Untitled';
        console.log(`📄 ${title} (${page.id})`);
    }
}

main().catch(console.error);
