# Final Thoughts Beyond the Scope of the Thesis

```{epigraph}
It just happened to be an unusual experience. By training I was a scientist: by vocation I was a writer.

-- C. P. Snow, _The Two Cultures_
```

```{epigraph}
[... Man] has no time to be anything but a machine. How can he remember well his ignorance--which his growth requires--who has so often to use his knowledge?

-- Henry David Thoreau, _Walden; or, life in the woods_
```

## Apology of the Thoughtful Dabbler

The work presented in this thesis is faceted, and placed at the intersection of hydrology, black-box optimization and HPC. For reasons of space and time, I focused just on the last.

Given the diversity of topics involved, the extent of the material, the time assigned to this project, its focus on HPC, and finally my background, I had to _use some tools_ (algorithms, concepts, etc.) without fully mastering them. This unavoidable fact is reflected in the frugality of the bibliography and in their presentation, which occasionally could be sloppy or contain plain errors. The responsibility for those is mine and mine only. However, I hope that the material presented here, if not the subject for more in-depth and broader research by the author, will be at least a prompt for more expert readers.

The growth of complexity in science, to which specialism was the universal response, is not going to decline; but maybe the compartmentalization of specialism will. When we will seek for systematic answers to the problems posed by this Cambrian explosion, one place to look will be computer science, which under many regards is the art of managing complexity by the human mind through abstractions. The simplest and most ubiquitous abstraction is the black box, and hence there is no shame in using black boxes when dealing with problems outside our competence. However, in order to make scientific statements about them, neglecting their inner workings, one needs the strictest rigour on the assumptions on their inputs and outputs.

It is unlikely that scientists will be replaced by scientific programmers in the future. However, good scientists surely will also be good programmers, i.e. they will be able to express elegantly both declarative knowledge by means of equations and of procedural knowledge, with the help of a computer.

## Rage Against Machine Learning

The main problem of present scientific research is the adoption of the ideas and methods from capitalist market economy. Research institutes must profit from the work of researchers and profit is measured by publications, funding, and patents. The phenomenon is not new, but the degree to which it permeates academia is unedited. Also, it is tightly linked to the sociopolitical and economic system in which we live, and it is probably irreversible. This problem not only intoxicates the academic environment and the life of people which work in academia, but also affects negatively the quality of research. It creates positive feedback loops and inflates some research topics while stagnating others. We live in a time of a profound, yet silent, crisis in science.

Of course, technology and applied science, which have an immediate return, are more likely to be funded and hence get more attention from researchers. In some cases, the situation is exacerbated by lack of scientific contents and rigour. Private investments in the loop worse the situation. 

Prominent examples of speculative bubbles are HPC and topics in machine learning as artificial neural networks. The latter deserves a word of caution. The ubiquitous application of artificial neural networks for modeling and inference, as surrogate human understanding, is the utmost failure of reductionism. We should invest more resources in their understanding, even if it is less rewarding than simply using them. Otherwise, the use of mathematical language, scientific method, and reductionism that fueled the most spectacular achievements in our understanding of nature is in danger.

Some problems in modern science requires HPC, although fewer than promised by exa-scale evangelists. Nonetheless, is it HPC an interesting scientific topic per se? I think that it is. Understanding the performance of large distributed systems, running thousands of coordinated processes simultaneously, is an interesting subject indeed. However, it needs a paradigm shift: it should be investigated for the sake of it, out of pure curiosity. The accent should be on comprehension, not on making things and doing stuff. Paradoxically, it is from gratuitous knowledge that the greatest technological advances come out, in the long run.

A related situation exists in computer science as a whole. Its cultural relevance and brief history rich of beautiful ideas are not recognized. As a consequence, programming is often taught and learned abysmally. The resources for these practices have no shortage of terms: tutorials, cookbooks, howtos. In the words of Kevlin Henney, from a [GOTO talk of 2018](https://www.youtube.com/watch?v=AbgsfeGvg3E).

> There's something else in software that we are particularly bad at: we have a very weak sense of history. So it is not simply that we keep rediscovering and reinventing the wheel, and eventually we might actually make it round; it's that we have a very poor cultural sense of history, and so we live in a constant state of astonishment and rediscovery.

At best, computer science is misunderstood, as wonderfully explained by Abelson and Sussman in their classic on the subject {cite}`abelson1996structure`.

> Underlying our approach to this subject is our conviction that "computer science" is not a science and that its significance has little to do with computers. The computer revolution is a revolution in the way we think and in the way we express what we think. The essence of this change is the emergence of what might best be called procedural epistemology--the study of the structure of knowledge from an imperative point of view, as opposed to the more declarative point of view taken by classical mathematical subjects. Mathematics provides a framework for dealing precisely with notions of "what is". Computation provides a framework for dealing precisely with notions of "how to".

If we don't free ourselves from utilitiarian views on computer science and programming, we will be doomed to poorly reinvent the wheel. Only when we will clearly see their beautiful ineffectiveness, we will be able to make progress.

In many research fields, articles, reviews, and conference proceedings account only for a part of the writing duty of researchers, the other being computer programs. Nonetheless, this is something for which they are not always given the proper credit. Furthermore, code is not always published, and its quality is not always at best. However, if programming is theory-building {cite}`naur1985programming`, then we need to consider code as literature and write correct, clear, reusable and extensively documented code to make real scientific progress and not waste our collective efforts.

The issue is not just the consideration we have for programming as an intellectual activity. If one wants to apply the scientific method to numerical experiments, he has to attain the same standards used for laboratory experiments: in other words, they must be reproducible. Hence, the reason of the importance of code and documentation in scientific computing is that they are part of the reproducibility effort.

## Math is the Ultimate Javascript Framework

I would go as far as saying that a playful interest in fundamental questions, beyond practical applications, is a good professional investment for a programmer too.

During the last Christmas holidays, I was chatting with my father about medium wave and longwave antennas. Since physical evidence is better than words, he suddenly went away and reappeared from the closet with a radio in his hand. It was a Grundig from the mid 80's. Once opened the back of the radio, the ferrite rod antenna and the long and medium wave windings were clearly visible. 

I was mesmerized and stared intensely at the inner of the radio. The whole circuitry contained less than ten bipolar junction transistors, for both amplitude and frequency modulation. I pointed with my finger at some components I wasn't able to recognize, and asked him what they were and why they were there, as I used to do as a kid. The strangest thing to me were the small radio frequency inductors. They had small red marks made with permanent ink. A long time before, he explained to me, he marked the original positions of the tuning screws, before trying to adjust the tune. A whole piece of the circuit board was covered with wax---which I thought was glue---, to avoid changing the position and orientation of some components, changing the inductance of the circuits and losing the right tuning. 

That world is gone[^howsad]. We now live in a world of integrated circuits. In our world, physical devices are assembled using tools similar to the ones found in software: abstractions. Black-boxes are combined, or replaced with equivalent ones. Most of the time, it is simply cheaper to use programmable electronics. 

[^howsad]: I can't help thinking how awfully sad this is. That world was beautiful and understandable. It was made of things you could tear apart and put back together, things that you could touch and smell, things that would let you the time to think.

This transformation is concerned with physical objects only to a lesser degree. The biggest shift was cultural. A generation of highly trained engineers has become obsolete. The knowledge and mental models they used were outdated. It has not happened during a century, but in few decades. It is highly unlikely that it will not happen again. Instead, if we extrapolate the trend, it is conceivable that the timescale of transformations will become shorter and shorter, due to technological acceleration.

In short, there are excellent chances that the knowledge about a particular technology that one acquires today will be worthless within the time span of his professional career[^frontend]. It is probable that our high-level code will look to future programmers like assembly looks to us today, i.e. something that should be generated and manipulated by machines. All the more reason for our carefully hand-unrolled loops considered as primitive as the monkeys screaming around the monolith in 2001: A Space Odissey by Stanley Kubrick[^monolith]. The GPT-3 model offers a hint of how this might happen.

[^frontend]: Frontend developers experience this inconvenience on a daily basis. However, here I am not really talking about javascript frameworks.

[^monolith]: Actually, this is true as of today.

Are we doomed to learn useless stuff? I think that the answer is no. Nonetheless, I think that learning a particular technology, which does not teach us something more general, is a waste of time. Details of implementation will come and go[^details], general questions will stay: the deeper the longer. Bartosz Milewski ends with the following words an article on his blog {cite}`milewski2020math` titled "Math is your insurance policy".

[^details]: As well as languages, libraries, compilers, and beloved compiler flags. 

> I’m often asked by programmers: How is learning category theory going to help me in my everyday programming? The implication being that it’s not worth learning math if it can’t be immediately applied to your current job. This makes sense if you are trying to locally optimize your life. You are close to the local minimum of your utility function and you want to get even closer to it. But the utility function is not constant–it evolves in time. Local minima disappear. Category theory is the insurance policy against the drying out of your current watering hole. 

We will need new tools however. From the preface of in Category Theory for Programmers {cite}`milewski2018category` 

> There is an unfinished gothic cathedral in Beauvais, France, that stands witness to this deeply human struggle with limitations. It was intended to beat all previous records of height and lightness, but it suffered a series of collapses. Ad hoc measures like iron rods and wooden supports keep it from disintegrating, but obviously a lot of things went wrong. From a modern perspective, it’s a miracle that so many gothic structures had been successfully completed without the help of modern material science, computer modelling, finite element analysis, and general math and physics. I hope future generations will be as admiring of the programming skills we’ve been displaying in building complex operating systems, web servers, and the internet infrastructure. And, frankly, they should, because we’ve done all this based on very flimsy theoretical foundations. We have to fix those foundations if we want to move forward.

```{bibliography}
:filter: docname in docnames
```
