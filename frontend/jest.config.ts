import type { Config } from 'jest';
import nextJest from 'next/jest.js';

const createJestConfig = nextJest({ dir: './' });

const config: Config = {
  coverageProvider: 'v8',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    // uuid ships as ESM — replace with a simple CJS stub for tests
    '^uuid$': '<rootDir>/__mocks__/uuid.ts',
  },
};

export default createJestConfig(config);
