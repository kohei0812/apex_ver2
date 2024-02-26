import function as func

start = 0
end = 33
page = func.scrape("https://apex.tracker.gg/apex/leaderboards/stats/all/RankScore?page=1&legend=all", start, end)

func.verify(page,start,end)
