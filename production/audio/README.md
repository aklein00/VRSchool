# Short faculty voice samples

Completed October 30, 2026. Arthur requested shorter teaching samples instead of the long saved voice previews, then asked for a wording and spoken-output review. The set contains 14 MP3s for 13 faculty, including separate Ettin Head A and Head B clips.

## Files

- `short-clips/`: current MP3s, transcripts, source manifest and speech-review results.
- `short-faculty-samples.json`: current scripts, saved voice assignments and clip metadata. Keep this production record outside the deployed site.
- `short-clips/archive/first-pass/`: superseded Science, PE, Art and Drama takes, preserved with the initial scripts.
- `elevenlabs-previews/`: earlier full-length preview copied before Arthur requested shorter clips; not used by the site.
- `../exports/VRHS-Short-Faculty-Voices.zip`: the 14 current MP3s and a transcript sheet.

## Voice assignments

Use the correctly named saved faculty voices, with Arthur's explicit exceptions:

- F04 Displacer Beast: `F06 Language Arts Brass Dragon`.
- F06 Brass Dragon: `F06 Brass Dragon Language Arts02`.
- F08 Gnoll: `F08 Gnoll PE 2`.
- F05 Ettin: `F05A Ettin Geography` and `F05B Geography Ettin` as two separate players.

## Website

The current selected MP3s are copied into `presentation-site/dist/assets/audio/` and wired into Prototypes. Each player has a transcript and an MP3 download link. Starting a clip pauses other gallery clips. No ElevenLabs login, API key or generation request is needed for website playback. The five student portrait entries remain planned voice studies because no matching saved student voices were supplied.

## Review

Scripts were reviewed for coherent standalone teaching points. Science, Physical Education, Art and Drama were rewritten and regenerated for clearer wording. Local speech-to-text checks compare the recordings with their scripts; this verifies spoken-word correspondence, not subjective acting quality. See `short-clips/speech-review.json` for the actual machine transcriptions. “Timber” in the Music transcription is the phonetic spelling of the musical term timbre; the published transcript uses the correct term.
