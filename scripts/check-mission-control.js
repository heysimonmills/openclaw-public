#!/usr/bin/env node
/**
 * Check Mission Control contents and see if it's the GJC teamspace
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
    console.log('=== Mission Control Contents ===\n');
    
    const missionControlId = '2f844b5e-ebe5-8117-ab7e-fce9b62c65ef';
    
    // Get Mission Control page content
    const content = await notionRequest(`/blocks/${missionControlId}/children`, GSG_TOKEN);
    
    console.log(`Found ${content.results?.length || 0} blocks:\n`);
    
    for (const block of content.results || []) {
        if (block.type === 'child_database') {
            console.log(`📊 Database: ${block.child_database?.title || 'Untitled'}`);
        } else if (block.type === 'child_page') {
            console.log(`📄 Page: ${block.child_page?.title || 'Untitled'}`);
        } else if (block.type === 'link_to_page') {
            const pageId = block.link_to_page?.page_id;
            console.log(`🔗 Link to page: ${pageId}`);
        } else {
            console.log(`⬜ ${block.type}`);
        }
    }
    
    // Search for any pages/databases with parent = Mission Control
    console.log('\n\n=== Children of Mission Control ===\n');
    
    const searchResults = await notionRequest('/search', GSG_TOKEN, {
        method: 'POST',
        body: { page_size: 100 }
    });
    
    const children = searchResults.results.filter(r => {
        return r.parent?.page_id === missionControlId ||
               r.parent?.database_id === missionControlId;
    });
    
    console.log(`Found ${children.length} children:\n`);
    
    for (const child of children) {
        const title = child.title?.[0]?.plain_text 
            || child.properties?.title?.title?.[0]?.plain_text
            || child.properties?.Name?.title?.[0]?.plain_text
            || 'Untitled';
        console.log(`${child.object.toUpperCase()}: ${title}`);
    }
}

main().catch(console.error);
