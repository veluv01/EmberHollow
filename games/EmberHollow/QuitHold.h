#pragma once
#include <stdint.h>
namespace eh {
// Wall-clock time keeps the deadline independent of frame rate. Unsigned
// subtraction also works across the millis() rollover.
struct QuitHold {
    uint32_t began=0;
    uint16_t elapsed=0;
    bool tracking=false;
    bool update(uint32_t now,bool held) {
        if(!held) { tracking=false;elapsed=0;return false; }
        if(!tracking) { tracking=true;began=now; }
        const uint32_t delta=now-began;
        elapsed=delta>=5000?5000:static_cast<uint16_t>(delta);
        return elapsed==5000;
    }
};
}
