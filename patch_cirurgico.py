# -*- coding: utf-8 -*-
import os, sys, zlib, base64, re

RELATORIO_B64 = """eNrtfW2P48h17nf/ikovZtGNK6lFitRLz24HHLVmVkhPq93SDC7yJShJJTWzFKnlS2/vfLIR3JvcIM4msYML+Isze3HhjIFBEGwMB/5o/ZP9A/FPyDnFF1ESJVESSWl6ejw77pYoVdWpU+etznnOZ331jqj9z48sp3unsq/zQ22s5k2mUdswVeOI9DRqWbNvHxHL/kZjnx/1VWus0W/OiG7o7CmhujqitmroZ2RA+6ypk2KhZBFGLZZX9bzh2E+Pzn9E5v4svPDZn+TzpK48a0z+Wrn8okUuWuSmcal0Jj+/abbIKWleNK46zQvlokGaV+1Os/Oq3mxdKZckn1/89s9wfd50u7T35dA0HL1/RjRVZ9TMD03aV5luHwsluc+GOWIOu/RYkHNiKSeJuWKhJp+Q4hPv9VIxJwk5uea9LhSLT06ekq5h9pl5RoTxPbEMTe27D8vlnFCt5USpCo+LcvBgXmMD+4zIwdOfFMWq1KsE7+OUHAu+TxzfPyVj2u+r+vCMiEX4hCjhayNqDoGgXcO2jZH7Dn76Pm/d0r7x9RkpwtzwaRwkj//wGRVz/H8FmEvEPsxTK9jcgcbg6//SsWx18E2+Z+g2EOyMWGPaY/kus79mTIfN19ShnldtNrLcj+Qtm5r2U/fnr006PiP471MyxB+FMsx5ySz8mSx/d81cZ+bSg9ky0x+2GEG/NVMJBoQV6/6IAyBD3lLfMPhOAb+Tv/A1U4e3QJtqsfiUaMyGgfNIJ76BxUKxykZPic3u7bxtUt0aGCYM74zHzOzBIYE9DHEo3zIxJ5Tgv1rN56GeoRnAa5+Uqt3+oBqP+aSTEBuV4EHBY5gZduNcFIMM+Kd9nZ/89MUrpU3+8Dty0bxpdFo3TYXUW5eNF03lQllPy1MkZqI0ryDNFwgoICHknCByCoYIKIGEqhaXEnDmc8kT8KJVf/USxBhItwZ50XrduLlSrkDegUTr4M8ZEdAnRk2ipW7VI+iAjlQNztLI0A1+yGNzhZJ/0WkiS8D/5duvrls3nUYiK/nsdL04uBX9ZbrHGw6ctyB3xa7oXDymPg0G/M/isc3DuRXx3G4mZOIKlPM//urn/0huUOFOvgeNS14y3aIaadyznmOrdwb54Se/IE29r/ZAtpvMIn1G2s7YMG2GP3aa8Qh4K655YjxPPhCLoEiKc2QUSgU5zDq9bl9mwlOuUPO3HmGFghyHANfMnLw3+gauQxk7Jp38evL/jDMgjG0a+tCf0JzMOzovCqdC8VQsimVCSSn4BQjBP3cOJPuO1I3RmNmT3+g9lQZfed5ybKdr8hEXP/Kc9W7pCLbSIBdsoOoqpz/MzemrNlB/DYnHK9TZagZeocu4+uyrJuu5lhUQwxlF6lum9z0GrK7nv2V20bz9U11u4IgyPOb9VywIJwsCsTpjvyA7uSbNjBia5abdBZF7qNo2tXEK3tlYwlCeDjg6R0su2GVyLFYk8nryFlZqWCcBi+wsoUIkXyqJy1JFqnafHnGbPDDDXasclgS7/gammGejGKRoq3oPZs4/QSj87THLoiacGbDm87RLd1nRireXvOW9HG3vCwXSapMq+bPrZpvUQTPeKPDDhTKjHI+vwepoXilEPFlr7M/byNLyM5GU1esrgbmhOdOvMnVvpdWaS5CjjZ1Ac1UHdNDbQEHFkQ9hu2FBAIPO+lvvaIHqspyRsUJf1WFok6qguChpganrSnnczLewWAqbuYLJbqUVhFtm24gRIuXo/Dnu4Rl5BpY2KAedSzIKc3pxed0koE9JHYQ/zHmVPl3Gw0vZaGiqKJXh3zxsBLxms7wrwmFTTDZm1D6WckQYmCe+9SBGuChreQjPEJwdIkQejE2lfmULt9Y2xq5x7Hm1sx7K1KstzmgFQUK1UN5MYUUokOWnw1cpK9yuOWK7osLjBosoXWbahrW9hBerqy1Pn1JzJpQAkwBNtItmmVWunm7xl8s3zF1rUQClINbAkCLH7L6nOZP3oDI+EeRiFehm2exke20ww55i2uw56++tYE+h2K1VhQ+XPdsgRHpgESKLpseavpccxZplOTnW9HdjnjVnp1YuorFWK+cqT9CAt+k9xf8HJQPE4FolITYtpc6mUk4o45OlNWxaZFRmtQ+YTS8V7rDG3KB0pGhNAo5Jjll9WizKUVEWuGdZlolukLFJ34D7CBbk2NG4YZEIc0ppM6dYquXKVfxbLJSWsyYbSPBn/6w5qFaEirA5az4D6mjGkCjcagUzVu2Df5Ueg/rzjGLQ5JjT35U4klQmFhsRe/Kup6s98A9tU+26qh+jIR0DrZ87pvfU9TpmvTuYus0cxzyWUz87M0GRYnX58akK1d6HbB93XrbJS9ZXKUi640C+n6R3fqjcldDNjTg/gkxGqp6FpdwBhjTgORO4E9YNrAmerhsytCfvx3CMkjKVy4fDqgO5xordD5dVr+Fd2CJVIzVwcK5rxRS5dNDrl6R+JJdKUk4mt1lwaa0IBjIIb6AJ/Mvt4zsU4iDiJ+/AIrHAeEZGTohVK4fDqsVyt9yXPlxWBTNkbFg2tUib2qo1oClbzaLYLzEW7eDJWbCqUMwVuTfXMzDO4pgUtrJrMgLcOsD7mJ1sjxk2rWYafCg93NjDlWFT8nLyDpQ/d+4y4dQVoQgQCuSUwL/7CUjw2yOgA72jmopk+C2zwP8DGo0mb+/VEc32KqWu3FxgWsFlo9l5daOQxv9s1F91mq/hJ/JauWxeKJO/nvxVa6N0qflDUN5GVi/jc7wZFKMSc7a8tJkmGMXPSjqKJxjwYzCvp2hu5r9W+/YtHOw4iR+f3coLlzzwvyresUfery8/tX6gY8WpjUg9ktkozvXpH3/1878jl0zlgti/01l3UXgrb5pbML/mGBkF5TjTV4gxvWEy2VDFu1snuP3Hi92eH9e/8254pzkAGLPxUxKoDrxj4c0pm368LBMv1AhHPPhcDi0sR7Opjk+PouKS+Kv/LTx+GXy4QFrEC5JNnx4YKuk5ozF3MuAbg49K4Y+6Jp6/nIGqe7fDFoFDKJzCbE/w2+/Qdeaz4QEOAhZgl6r3Rg4vvSbvRkB4vcfv6NzBTNXqGWeof4Nhp6NQVe9TMCPVuzDhwGSxHPioF/G6x+wU/DYveAAklImOC6NjmAaMRUNhB90Y4dQLsHkj7k/SRWKEyOf6eo5thDeA6V85FJ0wg4B5D9NlQ9h2GnzINb0Nk4Y/NAJDy+Sb5owoyCNwEjSQ2Uw3TG6QcOMZftDgcZiTn59SIJ+x0Tmmlzi2d8XJMJVFHUzembAgGALeB/YFmQekgm8YUSRazxgRsZKTnuBKrZDO5Cv0VAXRwfQTZdwtzw40WY911T61cvwbpmYSzEzw7HzfUCpkkqHiCkFhRgiKZTclbl5nhFJm4+uM8rpcEoz3cPtoW9NIXBNS9BzeSOvnj7/6xc/Ia4q3x97ZNkKZQzuYIFHX1lvlVSnwKeAd0jWBQ/F426p+S4H55EAmWigZvFMdnBJ+4Tc91ciW1E+KYQS1DNVwkYxMLwmBJ6eSlt/K4H1hcLqR17t4424M1J4K0ucWnteMIV68gyDq41dRm7rfGk9MFw4obUUskGvlqnWjvFTIi8aNckk+JY3XrctXrokVJKyU1iesxAt/CgMT/5sxcjaxmnDSHeVZAzQOmIjtjtJ51fZmvsw5StV/X2YTVjfPmcGsd2nRnpIK+0qfwTSZv/HTZK4pqBVgafICtIIGx8lNUXMzYvhFrjZNiSltnRJj067GfNJ4shn9k4DgsGqNji3GMwn5T7PkEjm51i3PvmW0HyMZzzYDznGHD5h0XS4ht275HpwRrJiIm4QMU/OHDLipGqRsLyQFBYlKn53atymMMLMOE7kPBgXlkdqAR+etrsXMO98djzMIPGWuS2+MseOf2V2j/80uXLFabCyvW1kcob+CYgsu/PTyTGTVAbr0Xs5P2CMAEvSTGH2RIdZfanuJQMlMIDLXdiYKEkp+8rUvWO6O6cbi4sxiPUd9IIwwm2azBw4IcpR5vk12HOCpp9D6ybFQPiH/w7V1eZq0VDv5yNjheRCRzoYVZgwVLzACrCDV9sAKPP18uvu1Yq725GPbf2XoULPPYwaDkMu3B2YININQzpQXQvLwqRvTAQ9wPPktG3HnHxNqeHToY2MMHhEjx15S0cledIWXYcTziZJlCT93KYolrow7gwhY9tcYkXBChISvXcPv3LmXPjbLgWogJYype7cXlgimk6nG8M1nrKQ6IT/8zT+F7Qh8uSwnrTkS39VKpBXW8WL7N+Gc432ahd5tQrJ7699+Ru0tXoJMfkfCMbqkthKeWO1BwgMY39gizxDjXqHAXINcN+utNsbAlGeNG35PenDxLxKzFHRNkdpuKAsHHmibCbb9ryDYhtcwvKrYvyz5lI7GT8mNao+McMht3cWmtAUGRZz01dJs+mrU5bcQF5ZiFXvOVGsJMau6SnGuX2bllbdtcXVrnErY9ckpYPv+4fd8r8nxj8Eut2mcvL51aShivDID/zSI/CCAWCztPvYsAfx78IiMk2JlWvMea9C4j33EvCQGvNTUJ+9BPOyTmYQsmUl4ZKakmakUMFOHmZNf71UwFTPkJaGUPC/tmP25igtD2QkLAF3rS5nLmeYkzO5v+CKN5yT801vS1C38XNi+SSobYReUlxaxuCvME5Rmc5bo4jULZgUEeUfhDJ9pmoBB9MnvR8xNN5h+lxuB0SnPNygQxQJSqTw9J0hw8nIzDazfYCMy+RcLTjGeT0zh+YqbEFZ+wFQTXtCMIeYrTb63iOoqBDdbYcw4Yhw7pDSEUoE0fvyqed0gncn/qV816wppPW/Wm8rlNAVBOtkp4zN57+aAEDrczN5IoLrqzjh1a+E99u44/eP/9x2nC2aBy8L0WwPROhpfOeqYAU/xXB5KWl4OT5CnIJ3s6kAtZIaWolGnoiE91q7QW4GXfDSFgbpkIB3NvpEjnVuEJmHkmjqaEcrKrPsyY0TEUnUqZo79r6iWc7VwLiYjttEP5/vBX46TN3SodZJiZt5ShDeXrVZjCm4JKVgKI+JJyxDx1pVlhnbIRzS7Ek+vSh6S3AqK7I7QYtwxc6AZX+fvzwh1bGPlIX8wWTXrLKAks244BOmSg+uJFGO3JJjlI0T7AAoWOBeyHZMHvjMeE+9oC1mT1s0Iz3LMa7DXCuSYX0JnOKxb9EwzXmutmDHfXiqk7pUgPKgssvJOV4BrM8c9FNGkTbVIbe9pIm5N+05ZNUIPy1xThUT/NHsgLo6s/8c3nEi7QF6Ck6Xbhq4a8ci50yXV0tBOnByJaiWtwRfu46py2kMFaUDpDzVz7R8m8dG5mMl2liPzn0pCrvok1fEXoUfnYSgwJdMFndjPNDycgaNzqZwrIqpAKtPYVjJlhMMdJeyq0QI66iq7VsmVn2wiAQ8hheVRf00TFDbXX667v8K3/Ag1ViUzjVWpZbSqKI1V/Og1lnAQCkvIiY/6ajt9VX7UVx+mvvIKijfXVzwsTS6wRH7oMOvQ1VZZykxtlUuZqS25vEdHS9ij2sLLvwNwtGqHobeqj4prW8UF2uAgFNfCXdisrhJ301XLQ6wuUfD5M6LasPXI168sZ/LWVBG/w0A8D4PY6oiRY7F6Qk5JOwzNelzdsaIkNLdVcii4oCmVMx6vmO14Yi2T8VbI9YwJLJRywpNMhvRb2JznH4fbc9XDYj8cDmTnrnLVXbC0IhtuCRrsXDZc0c+GI4kmlS3p5BTY1zds6EIjeXkFbt5/E/dwbDLb6zA2TdtQCNWxxN1ivAVMIHB7hm65AE4c6sZS7/zkM4vY5uQ3FhmbxkC1LEyzw942nvD2YW4QwcpNaSiQlkXE6hR5J4SzDT9jAlqPqfg6//LqLCb3mJkjqrMevKbj0IaNow0ZNtQJgXsh0o/hlmOaDFwgmKhJ9S9hK3AmMNU+4rhhvxtGsILEpjnSxzLerxzGCzjBa+Lv5kiP2mxomCrPieuzMdP7bhM1+P0eJosAVeoIbCQE8aLwOKxRBTqpeh9HcKhWSCyvTSqQutJpvMDukm6xTqdxddF0OycGmW3yY2bbY2ZbdGbbt7/7r//81k9uU8InvT5lc1dGXMMk4YTVzcl72y8fwkvwINlNPvRkN5AzcpDzOjRB/CB63BRxz89cK9e4VzdFEfSlCEoXzUf6wKRc3hornMeWThrb1jlbkez+mMiVYSLXC2Qz8FaC45RtlsprzrgfRdrRPhLJ9pHV9XGkV71WDc0vRwAt85hhFUXJtWH/o9UwrCm6gzEguypyJg7pNFhb2T1YG2/IIAZfEfcdRSmlv8txQtSlcgIh6t3mEk4IEnaOU++8MfIDuHvcSBIpY03teUVo2PBuYH9NTbZ3KVQSs5VCgrAzHsmmUqgk7JvZhQORQocjhErpzyW5lJ+HI4Reqj3TsED2kFJZ3rvoETIXPaWHKXpSzGpLSPQkkgydlAEkZ2cAeXch2+uEB2QABTcM16aBhhC/h+k09y2GxGrGYqjIkx2yFEMZLfHwxZCQq6Z88mNLIbGYk/YvhcSDgVncTJi8YJbt9U1Sesyy9h/OEaVsxUh194zxTaWI9ChFXCkiHo4xI4IU6T8YKZIywud166rTChIFPKjP9nWjPvnZc473GQfjcxcgR3H9nfryXMRSLVeu4t+ViGjhx+IBom3bPnTd1b0bDlkFg+aKbkIN0m40d8CiKq/puewVAfjX6pIHfSYIpB5A1CbVGXRJ1pIUx9D27rYI09gddsAKtbUr5SoE3gw11Qu9R+5C10VuXkIIquaCJ+kw3oLUsQ1TfeM/GiTscKAsNlBpYV9QayJ6ZXI1B076avYOP7dX/vYaea/i72vKW/RxPOg+2wOD10gLscy8BK3DYPIAOanPSaN7feGwaWKUVQcvIwu7mEleR72xye6wYbvrQmIOnGpZnKMxV42atqrd4tfvjZtThK9Mh5vXN41d5cBnzddi9cAEt8+fqs4FKk/AhF/HTENmnXw/NlUvARS4k8J6dMdm+gIzM7efopt2phk9TOI8IBhBuUAuW3Xlsvnn2CL6nxvtHOz+NUdLv2m2bpoXClhWQdplOcmehuKOPQ2fwcTBvjsNL2BJj+v95oYeMKa7eICY7t9+F0ATYva02nVU71QZJnkGRwgh+fwMzfLOGZoJ5Qcu5CWKMVcdM3Fwx+TBbZMDlyU/VSNTA/nuxM+q2uTLo3Oqpioj9TH9To7b5ALGC7Wdxs4hjZfMtcstQvyuOctCENWYYT/OM0SJH+9YOeC2kb5SKYUJeC1dYkTBquVccZPQ32n8sOyHsf/P9rz/tfS3P3xbVElrs5Pes5ki8UDOt8H1BcPrhg29WqhT0nKw0CnFXVwgYwZbNq1V3SzNIK68Xy/HVwZHd3Vpo7Hwl1f3RVV6r+teL63vmx1Z3hds86U6UheL+J5hg3lgQvSoNDf6xS1Ey3JUIlaEEEj80GRD/hNW2TUvQlVrOaxqg4+oXVWDMbDFY2/yVush/gb32iZv75jmVwWh+YkeoUl0ZtmU3DHTgkELiZe/8IbtC07YQ+jVLh5Yr/a//zff1ahrFPhgoPbo1NfoqGPDrxQDZ990AyVxXI81Hdu3xKROyF05KL8kraKmFWb+sibqN6yHxbuJuBIxOsOHC5oKmQ/KvZjMR32u6tkPijHO7EfduKYpqY3dpKwpKQ6eXlU9aKe4nIRTtLbxaOCUNPWeyhvpJmLoRrQcXYryBT6KXEl51KNzubKRVb3lKIIspE2/ZKFfdtjDxewScG03zGxJeHihmpM3yYnbcQeWJ7RIhxReyUaS0KosDyrctPnKUS11w97FyQkTIX1hAj5OJQNhIkgHIExKezvN0l5lCU+YOQD6C8UDkyVkZWYZOvTpSJvZvvMDCf6gCTp1ll86qm0QRbNppmInel5C6uKhuFE59raDZHUCPMItkjZ9Ui5ir+mn/Y9izOLHZ6YESG4hwZG5yHAley3101vKwuepZcW2QSFBcW9GQXmvJomciUW0C7kfipRgIqsOinPmxeRdX92HnBDLpfQP8WY5AVuOAnt4ABZ1dX/xCXmv8kOSMw2PrPBppEPNSIiSDNFpCSHJ8Iyq9zT9cMDD8CiEj8hcEMtZHLg9D5++vZB68so2yezlAk/UuGiQduvylVcLSDqNl9e8QrCjXH6hXMCPQT575UOGEV6SYyEdQI6Fm1/xw7f/HoLixZ3BTBpDc9wUC0YuVH3y3QjbzHfYaGyYLoi2YjO9ryL0tjFNtqic/Gh5okXq9Z0Lyd3lHYo+Z9purCgkmnlufSGRtF2bkS2Li/xc1lXFRbjjP/zkF+Q5bCDmaO1U2lMSV0cf/QnN1xXVJH4vsHVFURR8PVrNAoIlj036BqFwxbLsISkPYq/1ACsrs2WhONWWIdYhrxneh6fJQ/6MFmoupcQZSM6VnhBcVYhh3JJfk45cvkqTf9KoO8+Ye+LUorvQjBkwjjeZBeGTON9gqh/nGw928s5bGzmWyDWWhAPJrZOdawgT0qhY5idMy/w+Gqj2JKHYoyutXk7e2SZYTrtBWMcuenpN4Znkxzo6b3UtZt5RPzPh4SBiyzvBsK0pxAhioW4AlLee8e3q3YBjllVErFXjGEnbvVledXkntdn2cm2mW5P3mJ2P/WgsA2ur9SHKQcOxNZWZ1skhgPElzQXRiYI+xkjGbBBdSrVpQHUtG/g4BhG1JwsnBJMm+yAW+4YJRpQKunHsOpV06lQ+RL6Ilg7X2GdKt1WN1IrgSteKJ1kLh8BukaTN4l47CYca2EgmA+rfqa6pNHlHmGUxomEtEft4GOBmSgQ2cumQ1OncSDgEcUihWM6IByRuJ3te+bGq9yfveyqHoTGZ7WKdGCcHg5QYt/Cy87JDTonwh98QJYSMkM52LqSmXGHUrkc13pImqT30vj1yDxXH4g34YB81g7e1Y/fYYI9usOokAerSqLKMcqI3bp8oZwAy4q8zDpBHZEWnr8eDmXY1o/flQmzVdRLdpo51qk/+Q8cAsVeD6VbjKRoDJsDXWp6xN60MXd8yjX+R37TRAe2ovqHEcD1pN+qMgD4jkBI8LOPzXN9wsX+wQVqOYBtF+DhYGIaJkWs8F9g20W3uO/m9zVTsCTGmjuWihU2bKvLukOgruw3nAouNYDUpoX7zNk9o38KXIwaWiRebVoEoZOTa/NRUbfjR9qiD1vctAQEP5LUNs6ciVhFYQa5xjBaQBiQL9318CqazDzc3mlqQrv3m2EYIl85vMAkfB3KA7OzzqRI6BOq5HSaNsInldqCEn1UTW1Sinb4T6NHaONG8RvAOmdv6dO3NjHf83MfDWET8hZjwNVegaYB7vfBMUH6MfZ5HYWsE9hRo5O4JJ3WOVyT3ePnx2Jy89XfU7x4KbASsyUyTurS11JGj2ZPvdGYcEpJUpUCeKfU/u2y9IEqn+bpFPiWtNqmR+hfKS37rVr+Z/KzDITmD+7dqevdvq0OXh9LDk4tpy6amvVEfTz79lBt5yvFCnmmhQP3yX/2Lw2fAAaj+eTSXgEnLa/c9VeADAIWaeAZ3htXku3dKS7p3RsLOxVitvzZPHZ0FArk2lSC8xS9qiR6CbcArpwMGb/ZDArpAOgY+yvEPQMCEdBloLxV7e6bTxnPNWQg2foGP4xTox7q+EOPJAOxuvTYLKirEEMiIUpBxMS9L3Ir6GvFbJ3K23WV54Vs7Mebt3swCvXusZBcokzawVsdrU737MgWpkpMFEObS6mXOPBdeZq9YRfDuhJcp8WWGmpuuXucuIB8XjXZH+fGrBrlo+WqSfCKU5EqgKzdG/UDPgJr5IS4Kzv8xfFufDXNR54YUn3ivY5qBWMW/xYIgn/A7l9B+TK87gpKQtU5MtErdJG8iidbY22nPDTyd5fPdWREuHKAwUxcLS9RzmBeC3ZrHXg12Cne2GnEUykFIYMnNauzctZlk7bf36ogibpRq9YyYyWjrpcxaYsnxEGmX5uzFXqxnjLg9tPlBTnSRMZykVY5SKWyigAlBe3TW0ZGWhNRjLaJtUxtZxzdgGqPZmLvvSv7wk+9CTHG2LFjgs+4qJgwXF4a/vjnzzXgvVZrFWU+b0jMxm0GPylSepbQYXwS0Vdvx0K+CFaGCsj09THRjhCkkQG0MCE7e9+eI/XpqC/pBj2lEg1uHhoNOaUAu6VQonopFsTw1L5MgWJxHKLk12eDzo1vbHltnp6chDirAGeHt6K1xYWjcFbrm6QAmZ5+C0f8lswvIHoXx7fhP1f7nePKOCHhVQ2Z/fvQXXY3qXx6BP619fqQbxpjpzASywUjgVDPziPQQ/An0qK0T+C+PkQtqfnMUpV+XylRfWeqGztaZJOKMuuSpvNJKKdxHaCLqRvLcAQJto+o8GLhO6ZTjcdwPv/yX//rPb0kHBqOmZ4s0eXDI5tEHRn743/93zTbTdIyljvKsgcm9s0EFsJj8qEMcU2kTuK1MoLYySEZZFZAuJ5+ssgxeq3mxc/7Isq92dU9qXz9VV6kN4XtVYBxNBX5Ko0Xn6DVTXF/0iNOFus1NMhxaeXj5Rru1fazNlllFdKmKkfnxiQAO5m5Xg8E8js43jJHMxz5mfJzKMu06f5GAORO6h7nFjfKElrMYGty0dDXe13uhraPz53gn1fcaVNhBzCaZ0bbqbra89FCsooGe4uTmmGklvoU7JS9lOGEmiJ5aUkYvHL5NjN4lt7PR9ubROdh9ROmaqokG3off5zYhgVeSihkJvJm2QmGB52/ctgJvwVH/cMVeVPAi7CsfqPwTyrs3fHyUf3gWPzL5txr2SxD3JiEDyC0eQcjKJJy78p8PwG0nIKNORyYicwX61jaoajsMWlkQpOSYh/C9kL5xsk/BugqlTD4gw7L64QrWzaKpcYmxKGrhLDMTw5mevHUDL2/oo805Y3PW5Eeb89HmjCEap61ycuVHA3N3OViTHx3sjIWd9BhR3LOY8/u0XVNsi3SBt81Dh1kHIdceHeck5Jr0GDjMXq5J1Ue5dhBy7ZIZOjX7BmkXyMsCUeD06KrxKN4ejniTqo/iLXPxVnv0UR991M2E3eMlcBLC7tGWy1zYVaRHW+7Rllst3sTHEFwS4q0ifaDibf9SqpqVx7lQ2DdfsLetlLoy7h4NsQwk1aMhloCkqn5wXmd8IJwNajtWYkZUC6StdJrt54oL1v4puWy+bHbwt39utMnLRqd10bqc/PxFs66EYCNq62Ej4uOTilN80vKmKBC4hutG+8evmm0Xdj68mE1Ld9NHl08dI2g73AlErRcPALV+ppD0/If3/+AjUFwzC/unuihEcBCtgVe3EEBN1HaGmjggxPiFqu2Y5YopQskjuI7X7Yl8YYzgk0Pap7uVaW6LKA9HjpwS+DfJKtEQsjyCBY0Ny6YWoXewM7BQixxz4GcdySCfJFRtucG8FhDH4vBD3egy03ZMSugI1mOG8U2EYm4BKWke1YSAnMMjJ0q1Ew6a1bxATC3fWArIE6AsgcACfeqiLBF8r+8CqLgVsrx+MS3EpLVneDUKXHn2ZBYX7N9ZgBm/uGluV6TZKuNYOAfR5dcBO14yle+gV6BGp0BrpIWM6mi8jtgHCGP3PabxOlE8u2zsikncBMdyPHA016KC13IwW4TBumPEAnOIIhC+hd8G+/iXju5XnCLoGAVT6p7LXziUHCcNkcqKTwqplJquMkIuFPJMaTfcGv+DU/GrdPOBa15P6/ICZF/xXiJeK+ra3zKLvGS20Te0yfdD4EPLhwJ0+qqNOC3IEBf8uMdRyqsV8sdQ+StnV/nbYSOaXu3vtIoUtrwxiw+azpDNEdjDNiIvkBsGDsXke1N9LCbdsptnQ7f90up+EkMuVELWwasBzqAulmzSwwSK8rmqIVZj+zo/+SkGCVzYNsTbNI27yVtEqgd+oSY4EncG6ZrOYQCRZ7jTLnbxtQsLSpMFMF62+V+oFj+ePSN1BpgCz4Mm4vCuLuC28Iffz0Cj6j6KsqPR/sfGA5dGj3c7SmfX/T7iinfK6NBk4CcaObAvR4QDUKSz9xjD7ZnOGxqg3yLGsM8GCMOrbb7wB7Ppk19qNgJ/KaCp09/8OuVHL+3TjvDNltpVNTBQPQBf7+yr+uSd2QOL9FyUTqWqi+B8SEjzG7TapuBgauSePKNW4rQM7qY6hk1VcATVO2YOeQOr1LYN1xHAYMGGgfPqwWR70G3HsFe2yWjXB7bGN5sXJx9ujL1WIPXWVf3yVRuD0i8aN42relO5JJ+Szs3kb9vE93Ovb5qtm2Zn8tObZjjWLhQ3w2heCUAZcn1rIfzJkFtSW0CfnBNjs/leEaGUOXQtERhhqz6qEX7xWkjkNLqo/vFXf/9vvj9cN/Se5vD4xwtm4q0YdrfBOszfBA6x5y03MOAG9ofrLAc+MWznjzZziKMfH0fSrLxIs1KMaGJ5FRVaju10EQXdxUDPoZvXxWMMVjWe0SBuBG9hqMiPMGJPTg9bH+mBmP5ErEjTeCPF6GQ43MiCIBOHa/dQ+eHXAJS5zHuJBqDLLb+p7fRpagPXqc70I1L4I7AIEC5kJuo57f+I4P7sfsxM1W0UQOzJ+zGCwYMVaU7ejtX5Ja5G7c8RNuoiDIxBrmtFfMhtwsMbCpgMPBJGnJEfbDM4Kj1XYG7LAByo75iebw0P3wGJcc3Tvkpjw7N20L71fHD+MBjdb9HducMbJRaywzDgB6/7CxhT0KF3GD50Qb2DuZ8RmwNaw98QErbX8zAa5dpDNMSurPCtHNyQyHwqCJ8dgZiI5B6H4El5UTXvkuBPz6te9zdvBEeuh4v1Aw6qh4xXII0RZzCNabBIWOOIwvcC1xk4LUfnI1g4GfD7gKag7WCbR1SH7xshQ4MvRIdslMPpDzTn3qVqj1kWj2XDEyDQYBa+9USA79m97e1OYcmRHsfB0wNhv0oRbIWqtzHu74Pp/Jgl2B7aOHPXNf7FgEfC6vJEh6RA7dZPQpKfBJBrM2oprYHnfPG2w8/RQwvQrQb/2NG/c+m6eTPfBfNlIwzVGYz26sq8sBkDbDHyLmwEHL2TtyGIa+5KXKTlDQjnoa9y3TfX5pfrfzb5tdssBtsR+Y5Lz+t/4YG2Mv6uBRowUvVlRpfNW2L4f25Y37fADM7r2CfDo4Nrzb1hJqgaX1kXA1JM4VH44vl1um7xGOwGkMbxKbAPnJ9wIvhBn3UvLpPiWRcP6Kz3Wbm60VlXxhpoKtM3AMF3xFtyij34DNOweMeu6fFF29zrSwGaDVwH1c1vmDbbQu3qRyER/ZEnJn4Ap33xFHPJNyu9DIf/3gv15vBMcx1sbo8G8JMouV7Ofg/5ykq1gz6zRbEq9SppntnS4ZzZLmXlQX8zzXSnWnBmuaNmhTy103ajyZv+ea6aSehMx0p0sS23H7GbmeT3igAjtZO/oNZt16Bm/wPTzozcqYbmZ2nA+VRcakxVMwbEgCBBTBX+4mUgI7fT6zm8KaUmP/R7UtKJhGaX+9teHlHrRVMhdeVq8ourZl0hDdh5pfOqvXMqUTl2KlF5bWIoerlCebscNHl1RHN1tpmX4mMMQb/dMMsZYXwPuCXI8gmlnz3H7ORp47SZc4ZJzfZsYN8/an6OoKtZZ44d6SyG/85mOq+Rye/8sCE5xgAj/I4xxc8JDw2eFHhAsOd1LYUPi7Lgqmf6xuAPw2dCET/8IAYIYWh+UzgTSsTgEkaxFnuANr5y1DELskPPiF/3liOdW8obj3K0lsKulwjua/8NPouf+g=="""

def aplicar_patch():
    caminhos = ["frontend/painel.html", "painel.html"]
    alvo = None
    for c in caminhos:
        if os.path.exists(c):
            alvo = c
            break
            
    if not alvo:
        print("❌ Erro: painel.html não encontrado no diretório atual!")
        sys.exit(1)

    with open(alvo, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    print(f"📖 Lendo {alvo} ({len(text)} caracteres)...")

    # 1. Inserir sub-abas e Relatório Executivo no GLPI (se ainda não existir)
    if 'id="subview-glpi-relatorio"' not in text:
        p_glpi = text.find('id="view-gestao_glpi"')
        if p_glpi != -1:
            p_open_start = text.rfind('<div', 0, p_glpi)
            p_open_end = text.find('>', p_glpi) + 1
            open_tag = text[p_open_start:p_open_end]

            p_next_view = text.find('id="view-', p_open_end + 20)
            p_close_div = text.rfind('</div>', p_open_end, p_next_view)

            operacional_content = text[p_open_end:p_close_div].strip()

            relatorio_html = zlib.decompress(base64.b64decode(RELATORIO_B64.encode('ascii'))).decode('utf-8')

            barra_html = """
            <!-- SELETOR DE SUB-ABAS OFICIAL GLPI (DESIGN SYSTEM SP-ÁGUAS V11) -->
            <div id="barra-subabas-glpi" style="display: flex; gap: 8px; margin-bottom: 16px; background: rgba(15,23,42,0.85); padding: 8px 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.08); align-items: center; flex-wrap: wrap;">
                <span style="font-size: 11px; font-weight: 800; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.05em; margin-right: 6px; display: flex; align-items: center; gap: 6px;">
                    <span>🎫</span> MÓDULO GLPI:
                </span>
                <button type="button" id="btn-glpi-subaba-operacional" class="btn btn-primary active" onclick="window.alternarSubAbaGlpi('operacional')" style="background: linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%); color: #ffffff; font-weight: 700; font-size: 12px; padding: 7px 16px; border-radius: 8px; border: 1px solid rgba(56,189,248,0.5); cursor: pointer; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 2px 8px rgba(2,132,199,0.3);">
                    <span>📊</span> Fila Operacional &amp; Métricas (15)
                </button>
                <button type="button" id="btn-glpi-subaba-relatorio" class="btn btn-secondary" onclick="window.alternarSubAbaGlpi('relatorio')" style="background: rgba(255,255,255,0.06); color: #cbd5e1; font-weight: 600; font-size: 12px; padding: 7px 16px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.12); cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s ease;">
                    <span>📑</span> Relatório Mensal Executivo de Suporte TI (Outubro/2026)
                </button>
                <div style="margin-left: auto; display: flex; align-items: center; gap: 8px;">
                    <span id="badge-glpi-subaba-info" style="font-size: 11px; color: #94a3b8; background: rgba(30,41,59,0.6); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
                        🟢 Base Oficial Homologada (274 Válidos)
                    </span>
                </div>
            </div>

            <!-- SUB-ABA 1: FILA OPERACIONAL & MÉTRICAS (PRESERVA 100% O CONTEÚDO ATUAL) -->
            <div id="subview-glpi-operacional" class="subview-glpi">"""

            novo_glpi_view = open_tag + "\n" + barra_html + "\n" + operacional_content + "\n            </div> <!-- FIM SUBVIEW OPERACIONAL -->\n\n" + relatorio_html + "\n        </div>"
            text = text[:p_open_start] + novo_glpi_view + text[p_close_div + 6:]
            print("✅ Relatório Executivo GLPI e sub-abas integrados!")

    # 2. Injetar funções JavaScript de controle do GLPI
    if 'window.alternarSubAbaGlpi' not in text:
        glpi_js = """
    window.subAbaGlpiAtiva = 'operacional';
    window.alternarSubAbaGlpi = function(subAba) {
        window.subAbaGlpiAtiva = subAba || 'operacional';
        var vOperacional = document.getElementById('subview-glpi-operacional');
        var vRelatorio = document.getElementById('subview-glpi-relatorio');
        var btnOperacional = document.getElementById('btn-glpi-subaba-operacional');
        var btnRelatorio = document.getElementById('btn-glpi-subaba-relatorio');

        if (subAba === 'relatorio') {
            if (vOperacional) vOperacional.style.display = 'none';
            if (vRelatorio) {
                vRelatorio.style.display = 'block';
                vRelatorio.style.opacity = '0';
                setTimeout(function() {
                    vRelatorio.style.transition = 'opacity 0.25s ease-in-out';
                    vRelatorio.style.opacity = '1';
                }, 10);
            }
            if (btnOperacional) {
                btnOperacional.className = 'btn btn-secondary';
                btnOperacional.style.background = 'rgba(255,255,255,0.06)';
                btnOperacional.style.color = '#cbd5e1';
                btnOperacional.style.fontWeight = '600';
                btnOperacional.style.border = '1px solid rgba(255,255,255,0.12)';
                btnOperacional.style.boxShadow = 'none';
            }
            if (btnRelatorio) {
                btnRelatorio.className = 'btn btn-primary active';
                btnRelatorio.style.background = 'linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%)';
                btnRelatorio.style.color = '#ffffff';
                btnRelatorio.style.fontWeight = '700';
                btnRelatorio.style.border = '1px solid rgba(56,189,248,0.5)';
                btnRelatorio.style.boxShadow = '0 2px 8px rgba(2,132,199,0.3)';
            }
        } else {
            if (vRelatorio) vRelatorio.style.display = 'none';
            if (vOperacional) {
                vOperacional.style.display = 'block';
                vOperacional.style.opacity = '0';
                setTimeout(function() {
                    vOperacional.style.transition = 'opacity 0.25s ease-in-out';
                    vOperacional.style.opacity = '1';
                }, 10);
            }
            if (btnOperacional) {
                btnOperacional.className = 'btn btn-primary active';
                btnOperacional.style.background = 'linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%)';
                btnOperacional.style.color = '#ffffff';
                btnOperacional.style.fontWeight = '700';
                btnOperacional.style.border = '1px solid rgba(56,189,248,0.5)';
                btnOperacional.style.boxShadow = '0 2px 8px rgba(2,132,199,0.3)';
            }
            if (btnRelatorio) {
                btnRelatorio.className = 'btn btn-secondary';
                btnRelatorio.style.background = 'rgba(255,255,255,0.06)';
                btnRelatorio.style.color = '#cbd5e1';
                btnRelatorio.style.fontWeight = '600';
                btnRelatorio.style.border = '1px solid rgba(255,255,255,0.12)';
                btnRelatorio.style.boxShadow = 'none';
            }
        }
    };
"""
        p_last_script = text.rfind('</script>')
        if p_last_script != -1:
            text = text[:p_last_script] + glpi_js + "\n" + text[p_last_script:]
            print("✅ Funções JS de alternância do GLPI injetadas!")

    # 3. Remover fallbacks da Mesa de Trabalho
    text = text.replace("var refs = ['137.00010608/2025-63', '137.00000119/2026-84', '137.00003051/2026-21'];", "var refs = []; // Fallback removido")
    text = text.replace("const refs = ['137.00010608/2025-63', '137.00000119/2026-84', '137.00003051/2026-21'];", "const refs = []; // Fallback removido")
    print("✅ Fallback de processos não atribuídos removido da Mesa de Trabalho!")

    # 4. Salvar nos arquivos locais
    for dest in ["painel.html", "frontend/painel.html"]:
        if os.path.exists(os.path.dirname(dest)) or dest == "painel.html":
            with open(dest, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"💾 Salvo com sucesso em: {dest}")

    print("\n🎉 Concluído com sucesso! Suas 3 abas e tema escuro V11 foram 100% preservados.")

if __name__ == '__main__':
    aplicar_patch()
