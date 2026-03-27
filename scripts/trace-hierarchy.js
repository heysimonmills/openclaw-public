#!/usr/bin/env node
/**
 * Trace Mission Control page hierarchy
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

async function tracePage(pageId, depth = 0) {
    const indent = '  '.repeat(depth);
    
    try {
        const page = await notionRequest(`/pages/${pageId}`, GSG_TOKEN);
        const title = page.properties?.title?.title?.[0]?.plain_text 
            || 'Untitled';
        
        console.log(`${indent}📄 ${title} (${pageId})`);
        console.log(`${indent}   Parent type: ${page.parent?.type}`);
        
        if (page.parent?.page_id) {
            await tracePage(page.parent.page_id, depth + 1);
        } else if (page.parent?.type === 'workspace') {
            console.log(`${indent}   → WORKSPACE ROOT`);
        } else if (page.parent?.type === 'block_id') {
            console.log(`${indent}   → Block parent (likely synced block or similar)`);
        }
    } catch (e) {
        console.log(`${indent}   Error: ${e.message}`);
    }
}

async function main() {
    console.log('=== Tracing Page Hierarchy ===\n');
    
    const missionControlId = '2f844b5e-ebe5-8117-ab7e-fce9b62c65ef';
    await tracePage(missionControlId);
    
    // Also check if there are other top-level pages
    console.log('\n\n=== Searching for other top-level structures ===\n');
    
    // Search for pages that might be teamspace roots
    const searchResults = await notionRequest('/search', GSG_TOKEN, {
        method: 'POST',
        body: { query: '', page_size: 100 }
    });
    
    // Find pages that have block_id parents (common in teamspaces) or are high-level
    const interestingPages = searchResults.results.filter(r => {
        if (r.object !== 'page') return false;
        const parentType = r.parent?.type;
        return parentType === 'block_id' || parentType === 'workspace';
    });
    
    console.log(`Found ${interestingPages.length} pages with block/workspace parents:\n`);
    
    for (const page of interestingPages.slice(0, 20)) {
        const title = page.properties?.title?.title?.[0]?.plain_text 
            || 'Untitled';
        console.log(`${title} (${page.id})`);
        console.log(`  Parent: ${page.parent?.type}`);
    }
}

main().catch(console.error);
