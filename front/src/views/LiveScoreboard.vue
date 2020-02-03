<template>
    <div class="screen">
        <iframe
            src="https://panzi.github.io/Browser-Ponies/ponies-iframe.html#fadeDuration=500&volume=1&fps=25&speed=3&audioEnabled=false&dontSpeak=true&showFps=false&showLoadProgress=false&speakProbability=0.1&spawn.masked%20matterhorn=1&spawn.nightmare%20moon=1&spawn.princess%20cadance=1&spawn.princess%20cadance%20(teenager)=1&spawn.princess%20celestia=1&spawn.princess%20celestia%20(alternate%20filly)=1&spawn.princess%20celestia%20(filly)=1&spawn.princess%20luna=1&spawn.princess%20luna%20(filly)=1&spawn.princess%20luna%20(season%201)=1&spawn.princess%20twilight%20sparkle=1&spawn.queen%20chrysalis=1&spawn.roseluck=1&spawn.sapphire%20shores=1&spawn.screw%20loose=1&spawn.screwball=1&spawn.seabreeze=1&spawn.sheriff%20silverstar=1&spawn.shoeshine=1&spawn.shopkeeper=1&spawn.silver%20spoon=1&spawn.sindy=1&spawn.sir%20colton%20vines=1&spawn.slendermane=1&spawn.soigne%20folio=1&spawn.stella=1&spawn.sue%20pie=1&spawn.suri%20polomare=1&spawn.twist=1&spawn.walter=1&spawnRandom=1&paddock=false&grass=false"
            class="pony"
            width="640"
            height="480"
            frameBorder="0"
            scrolling="no"
            marginHeight="0"
            marginWidth="0"
            title="pony"
        />
        <live-scoreboard />
    </div>
</template>

<script>
import LiveScoreboard from '@/components/LiveScoreboard/Index';

export default {
    components: {
        LiveScoreboard,
    },
};
</script>

<style lang="scss" scoped>
.screen {
    width: 100%;
    height: 100%;
    background-color: black;
}

.pony {
    position: fixed;
    overflow: hidden;
    border-style: none;
    margin: 0;
    padding: 0;
    background: transparent;
    width: 100%;
    height: 100%;
}
</style>
