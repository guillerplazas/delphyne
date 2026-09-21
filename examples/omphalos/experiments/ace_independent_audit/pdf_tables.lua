-- Fixed relative widths keep report tables inside the printable page.
-- Used by pandoc in either agent harness; no benchmark data is transformed.
function Table(el)
  local modern = el.colspecs ~= nil
  local n = modern and #el.colspecs or #el.aligns
  local first = ""
  if modern and #el.head.rows > 0 and #el.head.rows[1].cells > 0 then
    first = pandoc.utils.stringify(el.head.rows[1].cells[1].contents)
  elseif not modern and #el.headers > 0 then
    first = pandoc.utils.stringify(el.headers[1])
  end
  local widths = {}
  if n == 5 and first == "Arm" then
    widths = {0.30, 0.10, 0.20, 0.16, 0.24}
  elseif n == 5 and first == "Validation arm" then
    widths = {0.12, 0.22, 0.22, 0.22, 0.22}
  elseif n == 5 and first == "Recipe" then
    widths = {0.30, 0.155, 0.17, 0.165, 0.21}
  elseif n == 5 and first == "Pipeline" then
    widths = {0.23, 0.14, 0.20, 0.22, 0.21}
  elseif n == 3 and first == "Arm" then
    widths = {0.08, 0.22, 0.70}
  elseif n == 3 then
    widths = {0.56, 0.22, 0.22}
  else
    for i = 1, n do widths[i] = 1 / n end
  end
  if modern then
    for i = 1, n do
      el.colspecs[i] = {el.colspecs[i][1], widths[i]}
    end
  else
    el.widths = widths
  end
  return el
end
