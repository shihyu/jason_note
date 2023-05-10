<script >import { context } from './utils.js';
export let value;
$: context(value);
</script>
<slot/>
