<template>
  <section class="hero">
    <div class="hero-text">
      <div class="kicker">欢迎使用</div>
      <h1 class="headline">AI智能报价系统（新版）</h1>
      <div class="desc">从这里进入新版入口模块；旧版功能仍保留在根路径。</div>
    </div>
  </section>

  <section class="grid">
    <el-card class="card" shadow="hover">
      <div class="card-body">
        <div class="icon">📁</div>
        <div class="meta">
          <div class="name">AI-LLM</div>
          <div class="hint">大模型能力与工具入口</div>
        </div>
      </div>
      <div class="actions">
        <el-button type="primary" disabled>进入</el-button>
      </div>
    </el-card>

    <el-card class="card" shadow="hover">
      <div class="card-body">
        <div class="icon">📁</div>
        <div class="meta">
          <div class="name">AI音乐</div>
          <div class="hint">音乐生成与素材处理</div>
        </div>
      </div>
      <div class="actions">
        <el-button type="primary" disabled>进入</el-button>
      </div>
    </el-card>

    <el-card class="card" shadow="hover">
      <div class="card-body">
        <div class="icon">📁</div>
        <div class="meta">
          <div class="name">AI语音</div>
          <div class="hint">语音合成与识别</div>
        </div>
      </div>
      <div class="actions">
        <el-button type="primary" disabled>进入</el-button>
      </div>
    </el-card>
  </section>
</template>

<script setup lang="ts">
// 这里先做“新版主页骨架”，后续可按产品设计逐步补齐入口与路由
</script>

<style scoped>
.hero {
  padding: 18px 0 10px;
}

.kicker {
  color: #92a4c9;
  font-size: 12px;
  letter-spacing: 0.08em;
}

.headline {
  margin: 8px 0 6px;
  font-size: 28px;
  font-weight: 900;
  color: #ffffff;
}

.desc {
  color: #b8c5e2;
  font-size: 14px;
}

.grid {
  margin-top: 18px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.card {
  border: 1px solid #232f48;
  background: #151e32;
  color: #e5e7eb;
}

.card :deep(.el-card__body) {
  padding: 16px;
}

.card-body {
  display: flex;
  gap: 12px;
  align-items: center;
}

.icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(19, 91, 236, 0.18);
  display: grid;
  place-items: center;
  font-size: 18px;
}

.name {
  font-weight: 800;
  color: #ffffff;
}

.hint {
  margin-top: 4px;
  font-size: 12px;
  color: #92a4c9;
}

.actions {
  margin-top: 14px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  align-items: center;
}

@media (max-width: 980px) {
  .grid {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}
</style>







