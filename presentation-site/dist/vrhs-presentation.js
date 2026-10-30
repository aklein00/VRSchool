const printButton = document.querySelector('#print-guide');
printButton?.addEventListener('click', () => window.print());

if (document.querySelector('[data-sequencer]')) {
  const beats = [...document.querySelectorAll('[data-step]')];
  const play = document.querySelector('#play-phrase');
  const feedback = document.querySelector('#phrase-feedback');
  const muteButton = document.querySelector('#mute');
  const names = ['Tap', 'Chime', 'Rest'];
  let pattern = [0, 0, 2, 0];
  let context;
  let master;
  let muted = false;
  let run = 0;
  let timers = [];
  function render() {
    beats.forEach((button, index) => {
      const value = pattern[index];
      button.querySelector('strong').textContent = names[value];
      button.classList.toggle('rest', value === 2);
      button.classList.toggle('chime', value === 1);
      button.setAttribute('aria-label', `Beat ${index + 1}: ${names[value]}. Activate to change`);
    });
  }
  function stop() {
    run++;
    timers.forEach(clearTimeout);
    timers = [];
    beats.forEach(button => button.classList.remove('playing'));
    play.textContent = 'Play phrase ▶';
  }
  function tone(value) {
    if (value === 2 || !context) return;
    const oscillator = context.createOscillator();
    const envelope = context.createGain();
    oscillator.type = value === 0 ? 'triangle' : 'sine';
    oscillator.frequency.setValueAtTime(value === 0 ? 196 : 587.33, context.currentTime);
    if (value === 0) oscillator.frequency.exponentialRampToValueAtTime(100, context.currentTime + 0.13);
    envelope.gain.setValueAtTime(0.0001, context.currentTime);
    envelope.gain.exponentialRampToValueAtTime(0.32, context.currentTime + 0.008);
    envelope.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + 0.23);
    oscillator.connect(envelope).connect(master);
    oscillator.start();
    oscillator.stop(context.currentTime + 0.25);
  }
  beats.forEach((button, index) => button.addEventListener('click', () => {
    stop();
    pattern[index] = (pattern[index] + 1) % 3;
    render();
    feedback.textContent = `Beat ${index + 1} is now ${names[pattern[index]].toLowerCase()}. Play your phrase to hear the change.`;
  }));
  play.addEventListener('click', async () => {
    if (play.textContent.startsWith('Stop')) {
      stop();
      feedback.textContent = 'Playback stopped. Change a beat or play again.';
      return;
    }
    try {
      const Audio = window.AudioContext || window.webkitAudioContext;
      if (!Audio) throw new Error('Audio unavailable');
      if (!context) {
        context = new Audio();
        master = context.createGain();
        master.gain.value = muted ? 0 : 0.7;
        master.connect(context.destination);
      }
      await context.resume();
      stop();
      const currentRun = run;
      play.textContent = 'Stop playback ■';
      feedback.textContent = 'Listen and watch the four beats.';
      pattern.forEach((value, index) => timers.push(setTimeout(() => {
        if (currentRun !== run) return;
        beats.forEach(button => button.classList.remove('playing'));
        beats[index].classList.add('playing');
        tone(value);
      }, index * 500)));
      timers.push(setTimeout(() => {
        if (currentRun !== run) return;
        stop();
        const rests = pattern.flatMap((value, index) => value === 2 ? [index + 1] : []);
        feedback.textContent = rests.length ? `Your phrase has ${rests.length === 1 ? 'a rest on beat' : 'rests on beats'} ${rests.join(', ')}. Try changing the pattern and listen again.` : 'Every beat has a sound. Try adding a rest to change the phrase.';
      }, 2100));
    } catch {
      stop();
      feedback.textContent = 'Audio could not start in this browser. You can still arrange the beat tiles.';
    }
  });
  document.querySelector('#reset-phrase').addEventListener('click', () => {
    stop(); pattern = [0, 0, 2, 0]; render();
    feedback.textContent = 'Teacher’s pattern restored: tap, tap, rest, tap. Beat three stays silent.';
  });
  muteButton.addEventListener('click', () => {
    muted = !muted;
    if (master) master.gain.value = muted ? 0 : 0.7;
    muteButton.setAttribute('aria-pressed', String(muted));
    muteButton.textContent = muted ? 'Unmute' : 'Mute';
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) stop(); });
}
