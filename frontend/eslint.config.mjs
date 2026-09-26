import nextFlat from 'eslint-config-next';

const eslintConfig = [
  ...nextFlat,
  {
    ignores: ['node_modules/**', '.next/**', 'out/**'],
  },
];

export default eslintConfig;
