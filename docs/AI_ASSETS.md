# AI-generated image assets

APOLO includes an initial OpenAI Images API adapter for PNG image assets such as game icons, thumbnails, UI art and 2D textures.

## Configuration

Set the API key in the server environment, not in source control:

```dotenv
OPENAI_API_KEY=your_api_key
APOLO_ALLOW_IMAGE_GENERATION=true
```

Image generation is disabled by default. Every generation call also requires `confirm_generation=true`. Image generation is billed by the image provider; review the current API pricing and your project budget before enabling it.

## MCP tool

`apolo_generate_image_asset` accepts a project, prompt, simple PNG filename, model, size and quality. It saves the generated image under `assets/ai_generated/` inside the selected project and returns a SHA-256 hash and usage metadata.

Default model: `gpt-image-2.6-sunburst`. `gpt-image-2.6-flare` is available for faster iteration. Supported sizes are `1024x1024`, `1536x1024`, `1024x1536` and `auto`; supported quality values are `low`, `medium`, `high`, `xhigh` and `max`.

Generated images are not automatically uploaded or published. Review the file first, then use `apolo_upload_asset` separately if you approve it. Roblox upload has its own independent opt-in and confirmation.

## Still pending

This provider currently generates raster images only. It does not generate 3D meshes, layered clothing, audio, music or animation data. Those modalities need their own provider adapters, file validation and moderation/licensing checks. No placeholder output is reported as a generated asset.
