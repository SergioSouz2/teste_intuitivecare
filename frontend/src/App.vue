<template>
  <div id="app">
    <Navbar />
    <main>
      <router-view />
    </main>
  </div>
</template>

<script>
import Navbar from './components/Navbar.vue'

export default {
  components: { Navbar }
}
</script>

<style>
body {
  margin: 0;
  font-family: Arial, sans-serif;
  background-color: #f5f5f5;
}

main {
  padding: 20px;
}
</style>
