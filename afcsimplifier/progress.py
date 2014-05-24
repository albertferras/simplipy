#!/usr/bin/python -u
#encoding:utf-8

import time
import sys

class split_list():
    def __init__(self, L, part_size):
        self.L = L
        self.n = part_size
        self.i = 0
    
    def __len__(self):
        return len(self.L) / self.n
    
    def __iter__(self):
        return self
    
    def next(self):
        i = self.i
        n = self.n
        if i*n >= len(self.L):
            raise StopIteration
        else:
            x = self.L[i*n:(i+1)*n]
            self.i += 1
            return x


class timemanager():
    def __init__(self, size=20):
        self.size = size
        
        self.times = [time.time()]
        self.items = [0]
        self.cnt = 0
        
    def _next_cnt(self):
        self.cnt += 1
        if self.cnt >= self.size:
            self.cnt = 0
    
    def last_time(self):
        return self.times[self.cnt]
    
    def add_time(self, seconds, items):
        self._next_cnt()
        if self.cnt >= len(self.times):
            self.times.append(seconds)
            self.items.append(items)
        else:
            self.times[self.cnt] = seconds
            self.items[self.cnt] = items
    
    def estimate_total(self, total_items):
        ips = None
        remaining_time = None
        if len(self.items) > 0:
            t = max(self.times) - min(self.times)
            n = max(self.items) - min(self.items)
            if t > 0:
                ips = n / t
                if total_items is not None and ips > 0:
                    items_left = total_items - self.items[self.cnt]
                    remaining_time = items_left / ips
        
        return (ips, remaining_time)

def _format_time(secs):
    gm = time.gmtime(secs)
    if secs < 60*60:
        return time.strftime("%M:%S", gm)
    else:
        res = time.strftime("%H:%M:%S", gm)
        days = secs // (60*60*24)
        if days:
            res = "%dd " % days + res
        return res

class bar():
    def __init__(self, iterable, size=None, stdout=True, title=False, delay=0.5, refresh_delay=3, name=None):
        # delay = update every X seconds
        # refresh_delay = number of times 'delay' has to happen until we print stats
        # stdout = write progress in stdout as text
        # title = write progress in terminal title
        # console = write progress in stdout
        # size = set progress bar total number of items
        
        self.name=name
        self._iterable = iterable
        self.size = None
        if size is not None:
            self.size = size
        else:
            try:
                self.size = len(iterable)
            except:
                pass
        
        self.stdout = stdout
        self.title = title
        self.delay = delay
        self.refresh_delay = refresh_delay
        self._last_output_len = 0
        
        
    def init_iteration(self):
        self.times = timemanager(size=20)
        self.start_time = time.time()
        self.last_time = self.start_time
        self.count = 0
        self.delay_cnt = 1
    
    def __iter__(self):
        try:
            self.init_iteration()
            self.show_status()
            
            for elem in self._iterable:
                self.last_time = time.time()
                if self.last_time - self.times.last_time() > self.delay:
                    self.times.add_time(self.last_time, self.count)
                    
                    if self.delay_cnt >= self.refresh_delay:
                        self.show_status()
                        self.delay_cnt = 0
                    self.delay_cnt += 1
                    
                self.count += 1
                yield elem
            if self.stdout or self.title:
                self.show_status()
                if self.stdout:
                    print ""
        except KeyboardInterrupt:
            raise
    
    def show_status(self):
        elapsed = self.last_time - self.start_time
        elapsed_str = _format_time(elapsed)
        n = self.count
        total = self.size
        (ips, remaining_time) = self.times.estimate_total(total)
        
        if ips is not None:
            ips_str = "%5.2f iters/sec" % ips
        else:
            ips_str = "? iters/sec"
        
        if total is None:
            fraction = 0.0
            # length unknown
            s = "%d/? [elapsed: %s left: ?, %s]"  % (n, elapsed_str, ips_str)
        else:
            if total == 0:
                fraction = 0
            else:
                fraction = (n+0.0) / total
            # length known
            width = len(str(total))
            percent = int(100 * fraction)
            left_str = _format_time(remaining_time)
            
            tmp = int(10 * fraction)
            bar = "|" + "#" * tmp + "-" * (10 - tmp) + "|"
            s = "%s%*d/%*d %3d%% [elapsed: %s left: %s, %s]" \
                % (bar, width, n, width, total, percent,
                   elapsed_str, left_str, ips_str)
        
        s = s[:80]
        if self.title is True:
            set_title_progress(n, total, name=self.name)
        if self.stdout is True:
            sys.stdout.write("\r%-*s\r" % (self._last_output_len, s))
        if self.title or self.stdout:
            sys.stdout.flush()
        self._last_output_len = len(s)

def set_title(name):
    windowt = '\033]2;%s\007' % name # Window titles
    screent = '\033k%s\033\\' % name # Screen TITLES (naming windows)
    sys.stdout.write("%s%s" % (windowt, screent))
    sys.stdout.flush()

def set_title_progress(n, total, name=None):
    if total == 0 or total is None:
        total = fraction = "?"
    else:
        fraction = "%.2f" % (100.0*n/total)
    if name is not None:
        pre = "%s: " % name
    else:
        pre = ""
    t = "%s%s / %s (%s%%)" % (pre, n, total, fraction)
    set_title(t)

if __name__ == "__main__":
    c = 0
    i = 0
    for x in bar(range(12000000)):
        i += 1
        c += x
    print "Total = %s" % c
    print "Real = %s" % sum(range(120))
    
        