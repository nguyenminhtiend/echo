import { betterAuth } from 'better-auth';

export const auth = betterAuth({
  database: {
    type: 'postgres',
    url: process.env.DATABASE_URL!,
  },
  emailAndPassword: {
    enabled: true,
  },
});
