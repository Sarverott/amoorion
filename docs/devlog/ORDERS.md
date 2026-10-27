# ORDERS

The author's answers to the open questions of [BRAINSTORM.md](BRAINSTORM.md).
Empty between batches.

### Q13
we need where to put our access data first
well... at now i placed `bw` command as package dependency inside tools with npm
let's begin with initializing our credentials been placed in .env - place them there
prepare me please livetests for all platforms under one command 
go ahead and try to connect with actual apis

### Q14
add deleting but with storage of what was deleted
same place will be for readed state of all posts currently are on each socialmedia
present them as json files with index for each profile in each platform (./platform/profile/*)
create dataset/ dir that is gitignored - there will be our data stored

### Q15
wait...
why we update packages that are not changed?
if package is not changed then leave version updating and bumping 
for example:
- if in next update we change something in main amoorion and blogger package
- then we bump version of both, rest we leave unchanged
- release carries only updated wheels if it is `Z` number change (`vX.Y.Z`) if `X` or `Y` all must be placed in release
- let's reduce calls to pypi, we still do not have couple of subpackages published yet
after that
- now we change accordingly docs and dev tools
- we do not bump rest, only these one whitch has changes... and the main amoorion, but if main amoorion is not changed then it is always `Z` bump


release of `X` stage will be after all current phases will be ended

every phase end is bump of `Y`

every step now should be bump of `Z`, pushed to origin dev branch, pull request created and automerged to master branch

after all workflows ends then pull it back to dev on origin and pulled to local repository