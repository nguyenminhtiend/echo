import {
  pgTable,
  uuid,
  varchar,
  text,
  integer,
  decimal,
  timestamp,
  jsonb,
} from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: varchar('email', { length: 255 }).unique().notNull(),
  name: varchar('name', { length: 255 }),
  role: varchar('role', { length: 50 }).default('user'),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
});

export const agentRuns = pgTable('agent_runs', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').references(() => users.id),
  task: text('task').notNull(),
  taskType: varchar('task_type', { length: 50 }),
  complexity: varchar('complexity', { length: 20 }),
  status: varchar('status', { length: 20 }).default('pending'),
  result: jsonb('result'),
  totalTokens: integer('total_tokens').default(0),
  totalCost: decimal('total_cost', { precision: 10, scale: 6 }).default('0'),
  durationMs: integer('duration_ms'),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
  completedAt: timestamp('completed_at', { withTimezone: true }),
});

export const costLedger = pgTable('cost_ledger', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').references(() => users.id),
  runId: uuid('run_id').references(() => agentRuns.id),
  model: varchar('model', { length: 100 }).notNull(),
  tokensIn: integer('tokens_in').notNull(),
  tokensOut: integer('tokens_out').notNull(),
  cost: decimal('cost', { precision: 10, scale: 6 }).notNull(),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
});
