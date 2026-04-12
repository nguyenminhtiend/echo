import {
  type AnyPgColumn,
  boolean,
  decimal,
  integer,
  jsonb,
  pgTable,
  text,
  timestamp,
  uuid,
  varchar,
} from 'drizzle-orm/pg-core';

/**
 * Identity tables — OWNED BY BETTER AUTH. These mirror the shape Better Auth
 * auto-migrates in ``apps/web/src/lib/auth.ts``; do not create/alter them
 * from this file. Column names are camelCase to match the DDL Better Auth
 * actually emits. Drizzle is used read-only here.
 */
export const user = pgTable('user', {
  id: text('id').primaryKey(),
  name: text('name').notNull(),
  email: text('email').unique().notNull(),
  emailVerified: boolean('emailVerified').notNull(),
  image: text('image'),
  createdAt: timestamp('createdAt', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updatedAt', { withTimezone: true }).defaultNow().notNull(),
});

export const session = pgTable('session', {
  id: text('id').primaryKey(),
  expiresAt: timestamp('expiresAt', { withTimezone: true }).notNull(),
  token: text('token').unique().notNull(),
  createdAt: timestamp('createdAt', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updatedAt', { withTimezone: true }).notNull(),
  ipAddress: text('ipAddress'),
  userAgent: text('userAgent'),
  userId: text('userId')
    .notNull()
    .references(() => user.id, { onDelete: 'cascade' }),
});

export const account = pgTable('account', {
  id: text('id').primaryKey(),
  accountId: text('accountId').notNull(),
  providerId: text('providerId').notNull(),
  userId: text('userId')
    .notNull()
    .references(() => user.id, { onDelete: 'cascade' }),
  accessToken: text('accessToken'),
  refreshToken: text('refreshToken'),
  idToken: text('idToken'),
  accessTokenExpiresAt: timestamp('accessTokenExpiresAt', { withTimezone: true }),
  refreshTokenExpiresAt: timestamp('refreshTokenExpiresAt', { withTimezone: true }),
  scope: text('scope'),
  password: text('password'),
  createdAt: timestamp('createdAt', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updatedAt', { withTimezone: true }).notNull(),
});

export const verification = pgTable('verification', {
  id: text('id').primaryKey(),
  identifier: text('identifier').notNull(),
  value: text('value').notNull(),
  expiresAt: timestamp('expiresAt', { withTimezone: true }).notNull(),
  createdAt: timestamp('createdAt', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updatedAt', { withTimezone: true }).defaultNow().notNull(),
});

/**
 * Application tables — OWNED BY ALEMBIC (``apps/api/src/db/alembic``).
 * ``user_id`` columns are ``text`` and FK Better Auth's ``user.id`` (cuid2).
 */
export const agentRuns = pgTable('agent_runs', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: text('user_id').references(() => user.id, { onDelete: 'set null' }),
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
  userId: text('user_id').references(() => user.id, { onDelete: 'set null' }),
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
  userId: text('user_id').references(() => user.id, { onDelete: 'set null' }),
  runId: uuid('run_id').references(() => agentRuns.id),
  model: varchar('model', { length: 100 }).notNull(),
  tokensIn: integer('tokens_in').notNull(),
  tokensOut: integer('tokens_out').notNull(),
  cost: decimal('cost', { precision: 10, scale: 6 }).notNull(),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
});
