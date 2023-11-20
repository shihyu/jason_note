## Vue

Sure, I'll provide you with a step-by-step guide assuming you're using a standard Vue CLI setup. If you don't have Vue CLI installed, you can install it globally using:

```
npm install -g @vue/cli
```

Now, let's assume you have a Vue CLI project set up or you want to create a new one. Follow these steps:

1. **Create a new Vue CLI project:**

   ```
   vue create my-vue-trading-app
   ```

   Replace `my-vue-trading-app` with the desired name for your project. Follow the prompts to set up your project.

2. **Navigate to your project folder:**

   ```
   cd my-vue-trading-app
   ```

3. **Install `vue-tradingview-widgets`:**

   ```
   npm install vue-tradingview-widgets
   ```

4. **Replace the content of `src/App.vue` with your template and script:**

   ```html
   <template>
     <div id="app">
       <Chart />
       <CryptoMarket />
       <Snaps />
       <Screener />
     </div>
   </template>
   
   <script>
   import { defineComponent } from 'vue';
   import { Chart, CryptoMarket, Snaps, Screener } from 'vue-tradingview-widgets';
   
   export default defineComponent({
     name: 'App',
     components: {
       Chart,
       CryptoMarket,
       Screener,
       Snaps,
     },
   });
   </script>
   
   <style>
   #app {
     font-family: Avenir, Helvetica, Arial, sans-serif;
     text-align: center;
     color: #2c3e50;
     margin-top: 60px;
   }
   </style>
   ```

5. **Run your Vue.js application:**

   ```sh
   bashCopy code
   npm run serve
   ```