import dotenv from 'dotenv';
dotenv.config();

import { handler } from '../../lambda/statuspage_updater.mjs';

(async () => {
  try {
    const result = await handler();
    console.log('Lambda executed successfully:', result);
  } catch (err) {
    console.error('Error executing lambda:', err);
    process.exit(1);
  }
})();
