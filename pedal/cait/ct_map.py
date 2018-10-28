class CtMap:
    """
    A cache implemented map using linear lists. This is a hold over from the javascript library when we couldn't be sure
    that a student's javascript could use maps.

    The design pattern used in this map is to always used the cached key/associated index. So methods accessing values
    will first call update_cache, and then use the fields self.cacheKey or self.cacheIndex.
    """

    def __init__(self):
        """
        :self.keys: The set of keys, each corresponds to the same index in values
        :self.values: The set of values, each corresponds to the same index in keys
        :self.cacheKey: the most recently used key, or None, if the value could not be found. This is kept in sync with
                        self.cacheIndex
        :self.cacheIndex: The most recently used index, or -1 if the value could not be found. This is kept in sync with
                            self.cacheKey
        """
        self.keys = []
        self.values = []
        self.cacheKey = None
        self.cacheIndex = -1

    def update_cache(self, key):
        """
        Updates the cache
        :param key: The key to be cached
        """
        if self.cacheIndex == -1 or self.cacheKey != key:
            self.cacheKey = key
            if key in self.keys:
                self.cacheIndex = self.keys.index(key)
            else:
                self.cacheIndex = -1

    def clear_cache(self):
        self.cacheKey = None
        self.cacheIndex = -1

    def clear(self):
        """
        Empties map and clears the cache
        """
        self.keys = []
        self.values = []
        self.clear_cache()

    def delete(self, key):
        """
        deletes value associated with the key, and then the key, in that order.
        :param key: The key to be deleted
        """
        self.update_cache(key)
        if self.cacheIndex != -1:
            del self.values[self.cacheIndex]
            del self.keys[self.cacheIndex]
        self.clear_cache()

    def get(self, key):
        self.update_cache(key)
        if self.cacheIndex == -1:
            raise IndexError(repr(key))
        return self.values[self.cacheIndex]
        
    def __getitem__(self, key):
        return self.get(key)

    def has(self, key):
        self.update_cache(key)
        return self.cacheIndex >= 0
        
    def __contains__(self, key):
        return self.has(key)

    def keys(self):
        return self.keys

    def values(self):
        return self.values

    def set(self, key, value):
        self.update_cache(key)
        if self.cacheIndex == -1:
            self.keys.append(key)
            self.values.append(value)
        else:
            self.values[self.cacheIndex] = value

    def size(self):
        return len(self.keys)

    def __str__(self):
        # return ''.join(["keys = ", self.keys.__str__(), ", values = ", self.values.__str__()])
        collector = ""
        for key, value in zip(self.keys, self.values):
            collector += '{}[{}: {}], '.format(collector, key, value)
            #collector = ''.join([collector, "[", key, ": ", value.__str__(), "], "])
        return collector

    def __repr__(self):
        collector = ""
        for key, value in zip(self.keys, self.values):
            collector = ''.join([collector, "[", key, ": ", value.__str__(), "], "])
        return collector
