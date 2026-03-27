#!/usr/bin/env node
/**
 * Search for teamspaces and top-level pages in GSG
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
    console.log('=== Searching for Teamspaces ===\n');
    
    // Get all pages with no filters
    const allResults = await notionRequest('/search', GSG_TOKEN, {
        method: 'POST',
        body: { page_size: 100 }
    });
    
    console.log(`Found ${allResults.results.length} total results\n`);
    
    // Filter for workspace-level pages (potential teamspaces)
    const workspacePages = allResults.results.filter(r => 
        r.object === 'page' && 
        r.parent?.type === 'workspace'
    );
    
    console.log('Workspace-level pages (potential teamspaces):');
    console.log('=' .repeat(50));
    
    for (const page of workspacePages) {
        const title = page.properties?.title?.title?.[0]?.plain_text 
            || page.properties?.Name?.title?.[0]?.plain_text
            || 'Untitled';
        
        console.log(`\n📁 ${title}`);
        console.log(`   ID: ${page.id}`);
        console.log(`   URL: ${page.url}`);
        
        // Get child pages
        try {
            const children = await notionRequest(`/blocks/${page.id}/children`, GSG_TOKEN);
            const childPages = children.results?.filter(c => c.type === 'child_page') || [];
            console.log(`   Child pages: ${childPages.length}`);
        } catch (e) {
            console.log(`   Child pages: (could not fetch)`);
        }
    }
    
    // Also search for anything with "teamspace" or "good jelly"
    console.log('\n\nSearching for teamspace-related content...');
    const teamspaceSearch = await notionRequest('/search', GSG_TOKEN, {
        method: 'POST',
        body: { 
            query: 'teamspace',
            page_size: 20
        }
    });
    
    console.log(`Found ${teamspaceSearch.results.length} teamspace-related results`);
    for (const result of teamspaceSearch.results) {
        const title = result.title?.[0]?.plain_text 
            || result.properties?.title?.title?.[0]?.plain_text
            || 'Untitled';
        console.log(`  - ${title} (${result.object})`);
    }
}

main().catch(console.error);
