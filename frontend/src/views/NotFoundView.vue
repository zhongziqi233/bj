<template>
  <div class="not-found">
    <h1>404</h1>
    <p>这个页面不存在。</p>
    <el-button type="primary" @click="$router.push('/today')">回到每日日志</el-button>
  </div>
</template>

<style scoped>
.not-found {
  display: grid;
  min-height: 100vh;
  place-content: center;
  justify-items: center;
  color: var(--od-text-strong);
  background:
    radial-gradient(circle at 50% 35%, rgba(97, 175, 239, 0.18), transparent 34rem),
    transparent;
}

.not-found h1 {
  margin: 0;
  font-size: 72px;
  color: transparent;
  background: linear-gradient(90deg, var(--od-blue), var(--od-purple), var(--od-cyan));
  background-size: 200% auto;
  -webkit-background-clip: text;
  background-clip: text;
  animation: titleShine 6s linear infinite;
}

.not-found p {
  margin: 4px 0 22px;
  color: var(--od-text-muted);
}
</style>
