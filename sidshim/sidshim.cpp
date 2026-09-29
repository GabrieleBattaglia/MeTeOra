// Interfaccia C minima su libsidplayfp 2.x, da chiamare con ctypes.
#include <sidplayfp/sidplayfp.h>
#include <sidplayfp/SidTune.h>
#include <sidplayfp/SidTuneInfo.h>
#include <sidplayfp/SidConfig.h>
#include <sidplayfp/SidInfo.h>
#include <sidplayfp/builders/residfp.h>
#include <cstring>
#include <new>

struct Lettore {
    sidplayfp motore;
    ReSIDfpBuilder costruttore{"sidshim"};
    SidTune *brano = nullptr;
    unsigned int frequenza = 48000;
    bool stereo = true;
    char errore[256] = {0};
};

extern "C" {

__declspec(dllexport) Lettore *sid_apri(const char *percorso, unsigned int frequenza, int stereo) {
    Lettore *l = new (std::nothrow) Lettore();
    if (!l) return nullptr;
    l->frequenza = frequenza;
    l->stereo = stereo != 0;
    l->costruttore.create(l->motore.info().maxsids());
    l->costruttore.filter(true);
    l->brano = new SidTune(percorso);
    if (!l->brano->getStatus()) {
        strncpy(l->errore, l->brano->statusString(), sizeof(l->errore) - 1);
    }
    return l;
}

__declspec(dllexport) const char *sid_errore(Lettore *l) {
    return l->errore[0] ? l->errore : nullptr;
}

// Restituisce il numero di sottobrani; iniziale e chip vanno in uscita.
__declspec(dllexport) int sid_info(Lettore *l, int *iniziale, int *chip) {
    const SidTuneInfo *i = l->brano->getInfo();
    if (!i) return 0;
    if (iniziale) *iniziale = (int)i->startSong();
    if (chip) *chip = (int)i->sidChips();
    return (int)i->songs();
}

// Seleziona il sottobrano (1..n) e riparte da zero. 0 se tutto bene.
__declspec(dllexport) int sid_scegli(Lettore *l, int sottobrano) {
    l->brano->selectSong((unsigned int)sottobrano);
    SidConfig c = l->motore.config();
    c.frequency = l->frequenza;
    c.playback = l->stereo ? SidConfig::STEREO : SidConfig::MONO;
    c.samplingMethod = SidConfig::INTERPOLATE;
    c.fastSampling = false;
    c.sidEmulation = &l->costruttore;
    if (!l->motore.config(c)) {
        strncpy(l->errore, l->motore.error(), sizeof(l->errore) - 1);
        return 1;
    }
    if (!l->motore.load(l->brano)) {
        strncpy(l->errore, l->motore.error(), sizeof(l->errore) - 1);
        return 2;
    }
    return 0;
}

// Riempie buf con campioni a 16 bit (interlacciati se stereo). Restituisce i campioni scritti.
__declspec(dllexport) int sid_rendi(Lettore *l, short *buf, int campioni) {
    return (int)l->motore.play(buf, (uint_least32_t)campioni);
}

__declspec(dllexport) void sid_chiudi(Lettore *l) {
    if (!l) return;
    l->motore.load(nullptr);
    delete l->brano;
    delete l;
}

}
