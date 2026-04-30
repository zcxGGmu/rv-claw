<template>
  <div class="diff-viewer">
    <div class="diff-viewer__header">
      <span class="diff-viewer__filename">{{ filename }}</span>
      <div class="diff-viewer__stats">
        <span class="diff-viewer__added">+{{ addedLines }}</span>
        <span class="diff-viewer__removed">-{{ removedLines }}</span>
      </div>
    </div>
    <div class="diff-viewer__content">
      <pre><code ref="codeRef">{{ diff }}</code></pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface Props {
  diff: string
  filename: string
}

const props = defineProps<Props>()

const addedLines = computed(() => {
  return (props.diff.match(/^\+[^+]/gm) || []).length
})

const removedLines = computed(() => {
  return (props.diff.match(/^-[^-]/gm) || []).length
})
</script>

<style scoped>
.diff-viewer {
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  overflow: hidden;
}

.diff-viewer__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: var(--el-fill-color-light);
  border-bottom: 1px solid var(--el-border-color);
}

.diff-viewer__filename {
  font-family: monospace;
  font-size: 14px;
}

.diff-viewer__stats {
  display: flex;
  gap: 12px;
}

.diff-viewer__added {
  color: var(--el-color-success);
}

.diff-viewer__removed {
  color: var(--el-color-danger);
}

.diff-viewer__content {
  padding: 16px;
  background-color: #1e1e1e;
  overflow-x: auto;
}

.diff-viewer__content pre {
  margin: 0;
  color: #d4d4d4;
  font-family: 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.5;
}
</style>
