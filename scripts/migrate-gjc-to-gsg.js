#!/usr/bin/env node
/**
 * Migrate Good Jelly Co Notion Workspace to GSG Workspace
 * Fixed version with proper status property handling
 */

const GJC_TOKEN = 'YOUR_NOTION_API_TOKEN';
const GSG_TOKEN = 'YOUR_NOTION_API_TOKEN';

// GSG Database IDs from config
const GSG_DATABASES = {
    tasks: '2f644b5e-ebe5-8079-9d9a-cf3f9b6aa62d',
    gjContentPlan: '2fa44b5e-ebe5-8115-8a44-c742824528cf'
};

// GJC Database IDs
const GJC_DATABASES = {
    contentPlan: '2a3c4c6b-a88a-8062-a413-e6ea537542d7',
    projects: '298c4c6b-a88a-8166-ab50-f72b421aa82f',
    editingTracker: '2c4c4c6b-a88a-80bd-b6bd-dc8143b96dd1',
    tasks: '298c4c6b-a88a-8199-adf0-d5e3c1f1bdda'
};

const HEADERS_GJC = {
    'Authorization': `Bearer ${GJC_TOKEN}`,
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
};

const HEADERS_GSG = {
    'Authorization': `Bearer ${GSG_TOKEN}`,
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
};

// Progress tracking
const migrationLog = {
    errors: [],
    created: [],
    skipped: [],
    migrated: [],
    stats: {
        databasesCreated: 0,
        entriesMigrated: 0,
        pagesCreated: 0,
        errors: 0
    }
};

function log(type, message, data = null) {
    migrationLog[type].push({ message, data, time: new Date().toISOString() });
    const emoji = type === 'errors' ? '❌' : type === 'created' ? '✅' : type === 'skipped' ? '⏭️' : '📦';
    console.log(`${emoji} ${message}`);
}

async function notionRequest(endpoint, headers, options = {}) {
    const url = `https://api.notion.com/v1${endpoint}`;
    const response = await fetch(url, {
        method: options.method || 'GET',
        headers: {
            ...headers,
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

// GJC API helpers
const gjc = {
    get: (endpoint) => notionRequest(endpoint, HEADERS_GJC),
    post: (endpoint, body) => notionRequest(endpoint, HEADERS_GJC, { method: 'POST', body }),
    patch: (endpoint, body) => notionRequest(endpoint, HEADERS_GJC, { method: 'PATCH', body }),
    queryDb: (dbId, body = {}) => notionRequest(`/databases/${dbId}/query`, HEADERS_GJC, { method: 'POST', body }),
    getDb: (dbId) => notionRequest(`/databases/${dbId}`, HEADERS_GJC),
    getPageContent: (pageId) => notionRequest(`/blocks/${pageId}/children`, HEADERS_GJC)
};

// GSG API helpers
const gsg = {
    get: (endpoint) => notionRequest(endpoint, HEADERS_GSG),
    post: (endpoint, body) => notionRequest(endpoint, HEADERS_GSG, { method: 'POST', body }),
    patch: (endpoint, body) => notionRequest(endpoint, HEADERS_GSG, { method: 'PATCH', body }),
    queryDb: (dbId, body = {}) => notionRequest(`/databases/${dbId}/query`, HEADERS_GSG, { method: 'POST', body }),
    getDb: (dbId) => notionRequest(`/databases/${dbId}`, HEADERS_GSG),
    createPage: (parent, properties, children = []) => notionRequest('/pages', HEADERS_GSG, {
        method: 'POST',
        body: { parent, properties, children }
    })
};

function cleanPropertyConfig(prop) {
    const type = prop.type;
    const config = prop[type];
    
    if (!config) return { [type]: {} };
    
    // Skip relation and rollup properties - they require valid database_ids
    // which we don't have until after migration
    if (type === 'relation') {
        console.log(`    ⚠️  Skipping relation property '${prop.name}' - must be recreated manually`);
        return null; // Signal to skip this property
    }
    
    if (type === 'rollup') {
        console.log(`    ⚠️  Skipping rollup property '${prop.name}' - must be recreated manually`);
        return null; // Signal to skip this property
    }
    
    // Handle status type - API doesn't allow options/groups on creation
    if (type === 'status') {
        // Status property is auto-created with default options
        return { status: {} };
    }
    
    if (type === 'formula') {
        console.log(`    ⚠️  Skipping formula property '${prop.name}' - formulas may reference other properties`);
        return null;
    }
    
    if (type === 'select') {
        return {
            select: {
                options: (config.options || []).map(opt => ({
                    name: opt.name,
                    color: opt.color
                }))
            }
        };
    }
    
    if (type === 'multi_select') {
        return {
            multi_select: {
                options: (config.options || []).map(opt => ({
                    name: opt.name,
                    color: opt.color
                }))
            }
        };
    }
    
    // For other types, return the type config as-is (but remove IDs where applicable)
    const cleanConfig = { ...config };
    delete cleanConfig.id;
    
    return { [type]: cleanConfig };
}

async function createDatabase(parentId, title, sourceDb, token) {
    const properties = {};
    const skippedProperties = [];
    let titlePropertyName = 'Name';
    
    for (const [key, prop] of Object.entries(sourceDb.properties)) {
        if (prop.type === 'title') {
            // Preserve the original title property name
            titlePropertyName = key;
            continue;
        }
        
        try {
            const cleaned = cleanPropertyConfig(prop);
            if (cleaned === null) {
                skippedProperties.push(key);
            } else {
                properties[key] = cleaned;
            }
        } catch (e) {
            console.log(`  ⚠️  Skipping property '${key}': ${e.message}`);
            skippedProperties.push(key);
        }
    }
    
    if (skippedProperties.length > 0) {
        console.log(`  ⚠️  Skipped properties (manual recreation needed): ${skippedProperties.join(', ')}`);
    }
    
    // Add title property with the original name
    properties[titlePropertyName] = { title: {} };
    
    console.log(`  ℹ️  Using title property: '${titlePropertyName}'`);
    
    const response = await notionRequest('/databases', {
        'Authorization': `Bearer ${token}`,
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }, {
        method: 'POST',
        body: {
            parent: { type: 'page_id', page_id: parentId },
            title: [{ type: 'text', text: { content: title } }],
            properties
        }
    });
    
    return response;
}

function transformEntryProperties(properties, schema) {
    const transformed = {};
    
    for (const [key, prop] of Object.entries(properties)) {
        const schemaProp = schema[key];
        if (!schemaProp) continue;
        
        const type = schemaProp.type;
        
        try {
            switch (type) {
                case 'title':
                    transformed[key] = {
                        title: prop.title?.map(t => ({
                            type: 'text',
                            text: { content: t.plain_text || t.text?.content || '' }
                        })) || [{ type: 'text', text: { content: '' } }]
                    };
                    break;
                    
                case 'rich_text':
                    transformed[key] = {
                        rich_text: prop.rich_text?.map(t => ({
                            type: 'text',
                            text: { content: t.plain_text || t.text?.content || '' }
                        })) || []
                    };
                    break;
                    
                case 'number':
                    if (prop.number !== null && prop.number !== undefined) {
                        transformed[key] = { number: prop.number };
                    }
                    break;
                    
                case 'select':
                    if (prop.select) {
                        transformed[key] = { select: { name: prop.select.name } };
                    }
                    break;
                    
                case 'multi_select':
                    transformed[key] = {
                        multi_select: prop.multi_select?.map(s => ({ name: s.name })) || []
                    };
                    break;
                    
                case 'date':
                    if (prop.date) {
                        transformed[key] = {
                            date: {
                                start: prop.date.start,
                                end: prop.date.end || undefined
                            }
                        };
                    }
                    break;
                    
                case 'checkbox':
                    transformed[key] = { checkbox: prop.checkbox || false };
                    break;
                    
                case 'url':
                    if (prop.url) {
                        transformed[key] = { url: prop.url };
                    }
                    break;
                    
                case 'email':
                    if (prop.email) {
                        transformed[key] = { email: prop.email };
                    }
                    break;
                    
                case 'phone_number':
                    if (prop.phone_number) {
                        transformed[key] = { phone_number: prop.phone_number };
                    }
                    break;
                    
                case 'status':
                    if (prop.status) {
                        transformed[key] = { status: { name: prop.status.name } };
                    }
                    break;
                    
                case 'relation':
                case 'rollup':
                case 'formula':
                case 'created_time':
                case 'created_by':
                case 'last_edited_time':
                case 'last_edited_by':
                    // Skip computed properties and relations
                    break;
                    
                case 'files':
                    if (prop.files && prop.files.length > 0) {
                        transformed[key] = {
                            files: prop.files.map(f => ({
                                name: f.name,
                                external: f.external ? { url: f.external.url } : undefined,
                                file: f.file ? { url: f.file.url, expiry_time: f.file.expiry_time } : undefined
                            })).filter(f => f.external || f.file)
                        };
                    }
                    break;
                    
                case 'people':
                    // Skip people properties (user IDs won't transfer)
                    break;
                    
                default:
                    console.log(`  ⚠️  Unknown property type '${type}' for '${key}'`);
            }
        } catch (error) {
            console.log(`  ⚠️  Could not transform property '${key}' (${type}): ${error.message}`);
        }
    }
    
    return transformed;
}

function transformBlocks(blocks) {
    if (!blocks || blocks.length === 0) return [];
    
    return blocks.map(block => {
        const type = block.type;
        
        try {
            switch (type) {
                case 'paragraph':
                    return {
                        object: 'block',
                        type: 'paragraph',
                        paragraph: {
                            rich_text: block.paragraph?.rich_text?.map(t => ({
                                type: 'text',
                                text: { content: t.plain_text || t.text?.content || '' }
                            })) || []
                        }
                    };
                    
                case 'heading_1':
                    return {
                        object: 'block',
                        type: 'heading_1',
                        heading_1: {
                            rich_text: block.heading_1?.rich_text?.map(t => ({
                                type: 'text',
                                text: { content: t.plain_text || t.text?.content || '' }
                            })) || []
                        }
                    };
                    
                case 'heading_2':
                    return {
                        object: 'block',
                        type: 'heading_2',
                        heading_2: {
                            rich_text: block.heading_2?.rich_text?.map(t => ({
                                type: 'text',
                                text: { content: t.plain_text || t.text?.content || '' }
                            })) || []
                        }
                    };
                    
                case 'heading_3':
                    return {
                        object: 'block',
                        type: 'heading_3',
                        heading_3: {
                            rich_text: block.heading_3?.rich_text?.map(t => ({
                                type: 'text',
                                text: { content: t.plain_text || t.text?.content || '' }
                            })) || []
                        }
                    };
                    
                case 'bulleted_list_item':
                    return {
                        object: 'block',
                        type: 'bulleted_list_item',
                        bulleted_list_item: {
                            rich_text: block.bulleted_list_item?.rich_text?.map(t => ({
                                type: 'text',
                                text: { content: t.plain_text || t.text?.content || '' }
                            })) || []
                        }
                    };
                    
                case 'numbered_list_item':
                    return {
                        object: 'block',
                        type: 'numbered_list_item',
                        numbered_list_item: {
                            rich_text: block.numbered_list_item?.rich_text?.map(t => ({
                                type: 'text',
                                text: { content: t.plain_text || t.text?.content || '' }
                            })) || []
                        }
                    };
                    
                case 'to_do':
                    return {
                        object: 'block',
                        type: 'to_do',
                        to_do: {
                            rich_text: block.to_do?.rich_text?.map(t => ({
                                type: 'text',
                                text: { content: t.plain_text || t.text?.content || '' }
                            })) || [],
                            checked: block.to_do?.checked || false
                        }
                    };
                    
                case 'quote':
                    return {
                        object: 'block',
                        type: 'quote',
                        quote: {
                            rich_text: block.quote?.rich_text?.map(t => ({
                                type: 'text',
                                text: { content: t.plain_text || t.text?.content || '' }
                            })) || []
                        }
                    };
                    
                case 'callout':
                    return {
                        object: 'block',
                        type: 'callout',
                        callout: {
                            rich_text: block.callout?.rich_text?.map(t => ({
                                type: 'text',
                                text: { content: t.plain_text || t.text?.content || '' }
                            })) || [],
                            icon: block.callout?.icon || { emoji: '💡' }
                        }
                    };
                    
                case 'divider':
                    return { object: 'block', type: 'divider', divider: {} };
                    
                default:
                    return null;
            }
        } catch (e) {
            return null;
        }
    }).filter(b => b !== null);
}

async function migrateDatabaseEntries(sourceDbId, targetDbId, sourceToken, targetToken) {
    const entries = [];
    let cursor = undefined;
    
    // Get source database schema
    const sourceDb = await notionRequest(`/databases/${sourceDbId}`, {
        'Authorization': `Bearer ${sourceToken}`,
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    });
    
    // Get all source entries
    do {
        const body = { page_size: 100 };
        if (cursor) body.start_cursor = cursor;
        
        const response = await notionRequest(`/databases/${sourceDbId}/query`, {
            'Authorization': `Bearer ${sourceToken}`,
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json'
        }, { method: 'POST', body });
        
        entries.push(...response.results);
        cursor = response.next_cursor;
        
    } while (cursor);
    
    console.log(`  Found ${entries.length} entries to migrate`);
    
    let successCount = 0;
    let errorCount = 0;
    
    for (let i = 0; i < entries.length; i++) {
        const entry = entries[i];
        try {
            const properties = transformEntryProperties(entry.properties, sourceDb.properties);
            
            // Get page content
            let children = [];
            try {
                const content = await notionRequest(`/blocks/${entry.id}/children`, {
                    'Authorization': `Bearer ${sourceToken}`,
                    'Notion-Version': '2022-06-28',
                    'Content-Type': 'application/json'
                });
                children = transformBlocks(content.results || []);
            } catch (e) {
                // Some entries might not have content blocks
            }
            
            // Create new entry
            await notionRequest('/pages', {
                'Authorization': `Bearer ${targetToken}`,
                'Notion-Version': '2022-06-28',
                'Content-Type': 'application/json'
            }, {
                method: 'POST',
                body: {
                    parent: { database_id: targetDbId },
                    properties,
                    children
                }
            });
            
            successCount++;
            process.stdout.write(`\r    Progress: ${i + 1}/${entries.length} (${successCount}✓ ${errorCount}✗)`);
            
        } catch (error) {
            errorCount++;
            const name = entry.properties?.Name?.title?.[0]?.plain_text || 
                        entry.properties?.['Task name']?.title?.[0]?.plain_text ||
                        entry.properties?.['Project name']?.title?.[0]?.plain_text ||
                        entry.id;
            log('errors', `Failed to migrate entry '${name}': ${error.message}`);
        }
    }
    
    console.log(`\n  ✅ Migrated ${successCount} entries (${errorCount} errors)`);
    migrationLog.stats.entriesMigrated += successCount;
    migrationLog.stats.errors += errorCount;
}

async function main() {
    console.log('=== Good Jelly Co to GSG Migration ===\n');
    
    try {
        // Step 1: Get source databases
        console.log('📊 Step 1: Fetching source database schemas...\n');
        
        const gjcDbs = {
            contentPlan: await gjc.getDb(GJC_DATABASES.contentPlan),
            projects: await gjc.getDb(GJC_DATABASES.projects),
            editingTracker: await gjc.getDb(GJC_DATABASES.editingTracker),
            tasks: await gjc.getDb(GJC_DATABASES.tasks)
        };
        
        console.log('Found GJC databases:');
        console.log(`  - GJ Content Plan: ${gjcDbs.contentPlan.title?.[0]?.plain_text} (${Object.keys(gjcDbs.contentPlan.properties).length} properties)`);
        console.log(`  - Projects: ${gjcDbs.projects.title?.[0]?.plain_text} (${Object.keys(gjcDbs.projects.properties).length} properties)`);
        console.log(`  - Editing Tracker: ${gjcDbs.editingTracker.title?.[0]?.plain_text} (${Object.keys(gjcDbs.editingTracker.properties).length} properties)`);
        console.log(`  - Tasks: ${gjcDbs.tasks.title?.[0]?.plain_text} (${Object.keys(gjcDbs.tasks.properties).length} properties)`);
        
        // Step 2: Find parent page in GSG
        console.log('\n📁 Step 2: Finding parent page in GSG...');
        
        const gsgSearch = await notionRequest('/search', HEADERS_GSG, {
            method: 'POST',
            body: { query: 'Teamspace Home', page_size: 1 }
        });
        
        let parentPageId;
        if (gsgSearch.results.length > 0) {
            parentPageId = gsgSearch.results[0].id;
            console.log(`  Using parent: ${gsgSearch.results[0].properties?.title?.title?.[0]?.plain_text || 'Teamspace Home'}`);
        } else {
            throw new Error('Could not find parent page in GSG');
        }
        
        // Step 3: Create Good Jelly Co Archive page
        console.log('\n📁 Step 3: Creating Good Jelly Co Archive page...');
        const archivePage = await gsg.createPage(
            { page_id: parentPageId },
            { title: { title: [{ text: { content: '🍯 Good Jelly Co Archive' } }] } }
        );
        console.log(`  ✅ Created archive page: ${archivePage.id}`);
        migrationLog.stats.pagesCreated++;
        
        // Step 4: Migrate databases
        console.log('\n🔄 Step 4: Migrating databases...\n');
        
        // 4a. GJ Content Plan - Compare with existing
        console.log('4a. GJ Content Plan:');
        try {
            const existingContentPlan = await gsg.getDb(GSG_DATABASES.gjContentPlan);
            console.log(`  Existing GJ Content Plan found: ${existingContentPlan.title?.[0]?.plain_text}`);
            
            // Compare properties
            const gjcProps = Object.keys(gjcDbs.contentPlan.properties).sort();
            const gsgProps = Object.keys(existingContentPlan.properties).sort();
            
            const onlyInGjc = gjcProps.filter(p => !gsgProps.includes(p));
            const onlyInGsg = gsgProps.filter(p => !gjcProps.includes(p));
            
            console.log(`  Properties only in GJC: ${onlyInGjc.join(', ') || 'none'}`);
            console.log(`  Properties only in GSG: ${onlyInGsg.join(', ') || 'none'}`);
            
            // Create a separate archive database for the old content
            console.log(`  Creating archive copy...`);
            const archiveDb = await createDatabase(archivePage.id, 'GJ Content Plan (Archive)', gjcDbs.contentPlan, GSG_TOKEN);
            console.log(`  ✅ Created archive database: ${archiveDb.id}`);
            migrationLog.stats.databasesCreated++;
            
            await migrateDatabaseEntries(GJC_DATABASES.contentPlan, archiveDb.id, GJC_TOKEN, GSG_TOKEN);
            
            log('migrated', 'GJ Content Plan - archived to separate database', { 
                sourceId: GJC_DATABASES.contentPlan, 
                archiveId: archiveDb.id,
                existingId: GSG_DATABASES.gjContentPlan
            });
        } catch (e) {
            if (e.message.includes('404')) {
                console.log(`  Creating new database...`);
                const newDb = await createDatabase(archivePage.id, 'GJ Content Plan', gjcDbs.contentPlan, GSG_TOKEN);
                console.log(`  ✅ Created: ${newDb.id}`);
                migrationLog.stats.databasesCreated++;
                await migrateDatabaseEntries(GJC_DATABASES.contentPlan, newDb.id, GJC_TOKEN, GSG_TOKEN);
                log('created', 'GJ Content Plan database', { id: newDb.id });
            } else {
                throw e;
            }
        }
        
        // 4b. Projects
        console.log('\n4b. Projects:');
        const projectsDb = await createDatabase(archivePage.id, 'GJC Projects', gjcDbs.projects, GSG_TOKEN);
        console.log(`  ✅ Created: ${projectsDb.id}`);
        migrationLog.stats.databasesCreated++;
        await migrateDatabaseEntries(GJC_DATABASES.projects, projectsDb.id, GJC_TOKEN, GSG_TOKEN);
        log('created', 'GJC Projects database', { id: projectsDb.id });
        
        // 4c. Editing Tracker
        console.log('\n4c. Editing Tracker:');
        const editingDb = await createDatabase(archivePage.id, 'GJC Editing Tracker', gjcDbs.editingTracker, GSG_TOKEN);
        console.log(`  ✅ Created: ${editingDb.id}`);
        migrationLog.stats.databasesCreated++;
        await migrateDatabaseEntries(GJC_DATABASES.editingTracker, editingDb.id, GJC_TOKEN, GSG_TOKEN);
        log('created', 'GJC Editing Tracker database', { id: editingDb.id });
        
        // 4d. Tasks
        console.log('\n4d. Tasks:');
        const tasksDb = await createDatabase(archivePage.id, 'GJC Tasks Archive', gjcDbs.tasks, GSG_TOKEN);
        console.log(`  ✅ Created: ${tasksDb.id}`);
        migrationLog.stats.databasesCreated++;
        await migrateDatabaseEntries(GJC_DATABASES.tasks, tasksDb.id, GJC_TOKEN, GSG_TOKEN);
        log('created', 'GJC Tasks Archive database', { id: tasksDb.id });
        
        // Step 5: Migrate Good Jelly HQ page
        console.log('\n📄 Step 5: Migrating Good Jelly HQ page...');
        const hqContent = await gjc.getPageContent('2c4c4c6b-a88a-801a-871d-cf5e35f44bb2');
        
        const newHqPage = await gsg.createPage(
            { page_id: archivePage.id },
            { title: { title: [{ text: { content: 'Good Jelly HQ (Archive)' } }] } },
            transformBlocks(hqContent.results)
        );
        console.log(`  ✅ Created: ${newHqPage.id}`);
        migrationLog.stats.pagesCreated++;
        log('created', 'Good Jelly HQ page', { id: newHqPage.id });
        
        // Summary
        console.log('\n' + '='.repeat(60));
        console.log('📋 MIGRATION SUMMARY');
        console.log('='.repeat(60));
        console.log(`\n📊 Statistics:`);
        console.log(`  - Databases created: ${migrationLog.stats.databasesCreated}`);
        console.log(`  - Entries migrated: ${migrationLog.stats.entriesMigrated}`);
        console.log(`  - Pages created: ${migrationLog.stats.pagesCreated}`);
        console.log(`  - Errors: ${migrationLog.stats.errors}`);
        
        console.log(`\n✅ Created: ${migrationLog.created.length}`);
        migrationLog.created.forEach(item => console.log(`   - ${item.message}`));
        
        console.log(`\n⏭️  Skipped: ${migrationLog.skipped.length}`);
        migrationLog.skipped.forEach(item => console.log(`   - ${item.message}`));
        
        if (migrationLog.errors.length > 0) {
            console.log(`\n❌ Errors: ${migrationLog.errors.length}`);
            migrationLog.errors.slice(0, 10).forEach(item => console.log(`   - ${item.message}`));
            if (migrationLog.errors.length > 10) {
                console.log(`   ... and ${migrationLog.errors.length - 10} more errors`);
            }
        }
        
        console.log('\n\n✨ Migration complete!');
        console.log(`\n🔗 Archive page: https://notion.so/${archivePage.id.replace(/-/g, '')}`);
        
        // Save migration log
        const fs = require('fs');
        fs.writeFileSync('/home/ubuntu/clawd/migration-log.json', JSON.stringify(migrationLog, null, 2));
        console.log('\n📝 Full migration log saved to: /home/ubuntu/clawd/migration-log.json');
        
    } catch (error) {
        console.error('\n❌ Fatal error:', error.message);
        console.error(error.stack);
        process.exit(1);
    }
}

main();
