<!-- Copyright 2022 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    https://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License. -->


<script lang="ts">
  // cloud function URLs imported from env variables 
  import { PUBLIC_UPLOAD_URL, PUBLIC_ANALYZE_URL, PUBLIC_GENERATE_URL } from "$env/static/public";
  // state variables 
  let inputFile: HTMLInputElement;
  let labels: string[] = [];
  let reactions: string[] = [];
  let loadingState: boolean = false;
  let uploadMessage: string = "";

  // function to handle file upload
  async function uploadImage() {
    if (inputFile.files !== null) {
      loadingState = true;
      const file = inputFile.files[0];
      const formData = new FormData();
      formData.append('file', file);

      // Upload the image to Cloud Storage
      const response = await fetch(PUBLIC_UPLOAD_URL, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      uploadMessage = data.message;

      if (response.ok) {
        // Analyze the uploaded image
        await analyzeImage(data.gcs_uri);
      } else {
        loadingState = false;
      }
    }
  }

  // function to analyze the uploaded image
  async function analyzeImage(gcsUri: string) {
    const response = await fetch(PUBLIC_ANALYZE_URL, {
      method: "POST",
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ gcs_uri: gcsUri }),
    });

    const data = await response.json();
    labels = data.labels;

    if (response.ok) {
      // Generate reactions based on labels
      await generateReactions(labels);
    } else {
      loadingState = false;
    }
  }

  // function to generate reactions based on labels
  async function generateReactions(labels: string[]) {
    const response = await fetch(PUBLIC_GENERATE_URL, {
      method: "POST",
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ labels }),
    });

    const data = await response.json();
    reactions = data.reactions;
    loadingState = false;
  }
</script>

<!-- head  -->
<svelte:head>
  <title>VisionLab</title>
</svelte:head>

<div class="bg-gray-400 min-h-screen">
  <!-- navbar  -->
  <div
    class="flex flex-row items-center space-x-4 bg-blue-300 text-white p-4 shadow-lg font-bold text-3xl mb-4 lg:mb-16"
  >
    <!-- google cloud logo  -->
    <img
      class="w-8 h-8"
      src="https://www.gend.co/hs-fs/hubfs/gcp-logo-cloud.png?width=730&name=gcp-logo-cloud.png"
      alt=""
    />
    <div>VisionLab</div>
  </div>
  <!-- image upload and processing area  -->
  <div
    class="flex flex-col lg:flex-row mx-4 space-y-6 lg:space-y-0 lg:mx-16 lg:justify-between"
  >
    <!-- file input  -->
    <div class="flex flex-col space-y-8 items-center justify-center">
      <label
        for="upload-file"
        class="bg-blue-600 cursor-pointer p-4 rounded-lg hover:scale-105 transition ease-in-out text-xl font-bold text-white"
        >Upload Image</label
      >
      <input
        id="upload-file"
        type="file"
        accept="image/*"
        on:change={uploadImage}
        bind:this={inputFile}
        hidden
      />
      <!-- upload message -->
      <div
        class="text-xl hover:scale-105 transition font-bold text-center bg-white text-blue-600 p-4 rounded-lg"
      >
        {uploadMessage}
      </div>
    </div>

    <!-- labels and reactions area -->
    <div class="flex flex-col space-y-8 items-center justify-center">
      <!-- loading state -->
      {#if loadingState}
        <div class="text-xl font-bold text-blue-600">Processing...</div>
      {/if}
      <!-- labels -->
      <div class="text-xl hover:scale-105 transition font-bold text-center bg-white text-blue-600 p-4 rounded-lg">
        Objects in the Image <br />
        {#each labels as label}
          <div>{label}</div>
        {/each}
      </div>
      <!-- reactions -->
      <div class="text-xl hover:scale-105 transition font-bold text-center bg-white text-blue-600 p-4 rounded-lg">
        Poosible learnings<br />
        {#each reactions as reaction}
          <div>{reaction}</div>
        {/each}
      </div>
    </div>
  </div>
  <!-- footer  -->
  <div
    class="bg-blue-600 flex-row flex text-white p-4 shadow-lg text-xl mt-4 lg:mt-16 sticky top-[100vh]"
  >
    <a
      href="https://github.com/bhaaratkrishnan/vertex-summarizer-svelte"
      target="_blank"
    >
      <div>Made by Udita</div>
    </a>
  </div>
</div>
