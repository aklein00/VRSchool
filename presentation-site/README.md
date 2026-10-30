# VRHS presentation website

This is a normal folder in aklein00/VRSchool, not a separate Git repository. Make website changes and commit them through the main VRSchool repository. Do not initialize a nested repository here.

## Vercel settings

- Repository: aklein00/VRSchool
- Root Directory: presentation-site
- Framework/Application Preset: Other
- Build Command: empty
- Output Directory: dist
- Install Command: empty
- Environment variables: none for this placeholder

Only dist is served as the website. It contains five HTML pages, shared CSS/JavaScript and five selected compressed concept images. Keep original artwork, research, workflows, voice assignments, secrets and project documents outside dist. Do not change the output directory to the VRSchool root.

## Pages

Pitch; Art Style Guide (eight disciplines); Prototypes; Design; Product. The production case study supports the pitch. Pending models, scenes and voice outputs are labeled. The four-beat interaction is a working browser sketch, not a complete 3D slice.

## Temporary preview

An earlier owner-private Sites preview is available separately. Its published content remains unchanged. Vercel and aklein00/VRSchool are the intended ongoing deployment route; do not recreate a nested Git repository for that old preview.

## Audio

The prototype synthesizes tones only after Play is pressed. It makes no ElevenLabs calls and uses no API keys or external runtime dependencies.
