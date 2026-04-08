import {
  type AnyPgColumn,
  decimal,
  integer,
  jsonb,
  pgTable,
  text,
  timestamp,
  uuid,
  varchar,
} from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: varchar('email', { length: 255 }).unique().notNull(),
  name: varchar('name', { length: 255 }),
  passwordHash: varchar('password_hash', { length: 255 }),
  role: varchar('role', { length: 50 }).notNull().default('user'),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
});

export const agentRuns = pgTable('agent_runs', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').references(() => users.id),
  task: text('task').notNull(),
  taskType: varchar('task_type', { length: 50 }),
  complexity: varchar('complexity', { length: 20 }),
  status: varchar('status', { length: 20 }).notNull().default('pending'),
  result: jsonb('result'),
  totalTokens: integer('total_tokens').notNull().default(0),
  totalCost: decimal('total_cost', { precision: 10, scale: 6 }).notNull().default('0'),
  durationMs: integer('duration_ms'),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  completedAt: timestamp('completed_at', { withTimezone: true }),
});

export const sessions = pgTable('sessions', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),
  sessionToken: varchar('session_token', { length: 255 }).notNull().unique(),
  expiresAt: timestamp('expires_at', { withTimezone: true }).notNull(),
});

export const traceEvents = pgTable('trace_events', {
  id: uuid('id').primaryKey().defaultRandom(),
  runId: uuid('run_id')
    .notNull()
    .references(() => agentRuns.id, { onDelete: 'cascade' }),
  parentId: uuid('parent_id').references((): AnyPgColumn => traceEvents.id),
  eventType: varchar('event_type', { length: 50 }).notNull(),
  agentName: varchar('agent_name', { length: 50 }),
  data: jsonb('data').notNull(),
  tokensIn: integer('tokens_in'),
  tokensOut: integer('tokens_out'),
  cost: decimal('cost', { precision: 10, scale: 6 }),
  durationMs: integer('duration_ms'),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
});

export const auditLog = pgTable('audit_log', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').references(() => users.id),
  action: varchar('action', { length: 100 }).notNull(),
  resource: varchar('resource', { length: 255 }),
  metadata: jsonb('metadata'),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
});

/** RAG chunks; embedding column (vector) exists in DB but is omitted — Drizzle has no native pgvector type here. */
export const ragChunks = pgTable('rag_chunks', {
  id: uuid('id').primaryKey().defaultRandom(),
  content: text('content').notNull(),
  chunkType: varchar('chunk_type', { length: 50 }),
  filePath: varchar('file_path', { length: 500 }),
  startLine: integer('start_line'),
  endLine: integer('end_line'),
  metadata: jsonb('metadata'),
  indexedAt: timestamp('indexed_at', { withTimezone: true }).defaultNow().notNull(),
});

export const graphNodes = pgTable('graph_nodes', {
  id: varchar('id', { length: 255 }).primaryKey(),
  label: varchar('label', { length: 100 }).notNull(),
  properties: jsonb('properties'),
});

export const graphEdges = pgTable('graph_edges', {
  id: uuid('id').primaryKey().defaultRandom(),
  sourceId: varchar('source_id', { length: 255 })
    .notNull()
    .references(() => graphNodes.id),
  targetId: varchar('target_id', { length: 255 })
    .notNull()
    .references(() => graphNodes.id),
  relation: varchar('relation', { length: 100 }).notNull(),
  properties: jsonb('properties'),
});

export const costLedger = pgTable('cost_ledger', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').references(() => users.id),
  runId: uuid('run_id').references(() => agentRuns.id),
  model: varchar('model', { length: 100 }).notNull(),
  tokensIn: integer('tokens_in').notNull(),
  tokensOut: integer('tokens_out').notNull(),
  cost: decimal('cost', { precision: 10, scale: 6 }).notNull(),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
});
