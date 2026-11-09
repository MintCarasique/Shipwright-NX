// Force-included into every soh translation unit on Nintendo Switch.
#pragma once

// newlib's <sys/types.h> defines BSD relics `quad` and `physadr` as macros when
// __BSD_VISIBLE is set. That silently renames struct members such as
// ColliderQuadDim::quad depending on include order, so pull the header in up
// front and drop the macros for good.
#include <sys/types.h>
#undef quad
#undef physadr
