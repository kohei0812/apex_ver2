import function as func

start = 33
end = 66
page = func.scrape("https://apex.tracker.gg/apex/leaderboards/stats/all/RankScore?page=1&legend=all", start, end)

func.verify(page, start, end)
