from vmi.db.pickler import Pickler
from vmi.model.show import ShowMetadata

def test_pickler(tmpdir):
	pickler = Pickler(tmpdir)
	show_metadata = ShowMetadata("Test Show", "test-show", 8.7, "tt1234567", 3)
	assert(not pickler.has(show_metadata))
	pickler.put(show_metadata)
	assert(pickler.has(show_metadata))
	gotten = pickler.get(show_metadata)
	# use hacky deep copy to check for equality
	assert(gotten.__dict__ == show_metadata.__dict__)